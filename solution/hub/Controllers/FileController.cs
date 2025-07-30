using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using System.Text;
using System.Text.Json;
using hub.Interfaces;
using hub.Dtos;
using FileModel = hub.Models.File;

namespace hub.Controllers
{
    [ApiController]    
    [Authorize]
    public class FileController : ControllerBase
    {
        private readonly IFileRepository _fileRepository;
        private readonly ILogger<FileController> _logger;
        private readonly IConfiguration _configuration;
        private readonly HttpClient _httpClient;

        public FileController(IFileRepository fileRepository, ILogger<FileController> logger, IConfiguration configuration, HttpClient httpClient)
        {
            _fileRepository = fileRepository;
            _logger = logger;
            _configuration = configuration;
            _httpClient = httpClient;
        }

        /// <summary>
        /// Obtiene todos los archivos del usuario logueado
        /// </summary>
        /// <returns>Lista de archivos del usuario autenticado</returns>
        [HttpGet("files")]
        public async Task<ActionResult<IEnumerable<FileResponseDto>>> GetAllFiles()
        {
            try
            {
                // Obtener el ID del usuario desde los claims del JWT
                var userIdClaim = User.FindFirst("userId") ?? User.FindFirst(ClaimTypes.NameIdentifier);
                if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
                {
                    _logger.LogWarning("No se pudo obtener el ID del usuario desde el token JWT");
                    return Unauthorized("Token inválido");
                }

                // Obtener archivos usando el repositorio
                var files = await _fileRepository.GetFilesByUserIdAsync(userId);

                _logger.LogInformation("Se obtuvieron {Count} archivos para el usuario {UserId}", files.Count(), userId);
                return Ok(files);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al obtener la lista de archivos del usuario");
                return StatusCode(500, "Error interno del servidor al obtener los archivos");
            }
        }

        /// <summary>
        /// Sube un archivo CSV o TXT y lo almacena con estado Pending
        /// </summary>
        /// <param name="file">Archivo CSV o TXT a subir</param>
        /// <returns>Información del archivo subido</returns>
        [HttpPost("upload")]
        public async Task<ActionResult<FileUploadResponseDto>> UploadFile(IFormFile file)
        {
            try
            {
                // Obtener el ID del usuario desde los claims del JWT
                var userIdClaim = User.FindFirst("userId") ?? User.FindFirst(ClaimTypes.NameIdentifier);
                if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
                {
                    _logger.LogWarning("No se pudo obtener el ID del usuario desde el token JWT");
                    return Unauthorized("Token inválido");
                }

                // Obtener el email del usuario desde los claims del JWT
                var emailClaim = User.FindFirst(ClaimTypes.Email);
                if (emailClaim == null || string.IsNullOrEmpty(emailClaim.Value))
                {
                    _logger.LogWarning("No se pudo obtener el email del usuario desde el token JWT");
                    return Unauthorized("Token inválido - email no encontrado");
                }

                // Validaciones del archivo
                if (file == null || file.Length == 0)
                {
                    return BadRequest("No se ha enviado ningún archivo o el archivo está vacío");
                }

                // Validar extensión del archivo
                var allowedExtensions = new[] { ".csv", ".txt" };
                var fileExtension = Path.GetExtension(file.FileName).ToLowerInvariant();
                if (!allowedExtensions.Contains(fileExtension))
                {
                    return BadRequest("Solo se permiten archivos CSV y TXT");
                }

                // Validar tamaño del archivo (máximo 10MB)
                const long maxFileSize = 1 * 1024 * 1024; // 1 MB
                if (file.Length > maxFileSize)
                {
                    return BadRequest("El archivo no puede exceder 10MB");
                }

                // Configurar la ruta de almacenamiento
                var uploadsPath = GetUploadsPath();

                // Guardar archivo físico usando el repositorio
                var filePath = await _fileRepository.SavePhysicalFileAsync(file, userId, uploadsPath);

                // Crear registro en la base de datos usando el repositorio
                var fileRecord = new FileModel
                {
                    TotalLinks = 0, // Se calculará cuando se procese
                    FilePath = filePath,
                    FileName = file.FileName,
                    TotalProcessed = 0,
                    TotalFailed = 0,
                    Status = "PENDING",
                    UploadedAt = DateTime.UtcNow,
                    UserId = userId
                };

                var createdFile = await _fileRepository.CreateFileAsync(fileRecord);

                // Enviar petición POST al servicio de procesamiento
                var processResponse = await SendProcessRequest(emailClaim.Value, createdFile.Id);
                
                var response = new FileUploadResponseDto
                {
                    Id = createdFile.Id,
                    FileName = createdFile.FileName,
                    Status = createdFile.Status,
                    UploadedAt = createdFile.UploadedAt,
                    Message = processResponse ? 
                        "Archivo subido exitosamente y enviado para procesamiento" : 
                        "Archivo subido exitosamente pero no se pudo enviar para procesamiento"
                };

                _logger.LogInformation("Archivo {FileName} subido exitosamente por usuario {UserId} con ID {FileId}", 
                    file.FileName, userId, createdFile.Id);

                return CreatedAtAction(nameof(UploadFile), new { id = createdFile.Id }, response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al subir archivo {FileName}", file?.FileName ?? "desconocido");
                return StatusCode(500, "Error interno del servidor al subir el archivo");
            }
        }

        /// <summary>
        /// Obtiene todos los links asociados a un archivo específico del usuario logueado
        /// </summary>
        /// <param name="fileId">ID del archivo</param>
        /// <returns>Lista de links del archivo</returns>
        [HttpGet("files/{fileId}/links")]
        public async Task<ActionResult<IEnumerable<LinkResponseDto>>> GetFileLinks(int fileId)
        {
            try
            {
                // Obtener el ID del usuario desde los claims del JWT
                var userIdClaim = User.FindFirst("userId") ?? User.FindFirst(ClaimTypes.NameIdentifier);
                if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out int userId))
                {
                    _logger.LogWarning("No se pudo obtener el ID del usuario desde el token JWT");
                    return Unauthorized("Token inválido");
                }

                // Verificar que el archivo pertenece al usuario logueado
                var fileExists = await _fileRepository.GetFileByIdAndUserIdAsync(fileId, userId);
                if (fileExists == null)
                {
                    _logger.LogWarning("Usuario {UserId} intentó acceder al archivo {FileId} que no le pertenece o no existe", userId, fileId);
                    return Unauthorized("No tienes permisos para acceder a este archivo");
                }

                // Obtener links del archivo usando el repositorio
                var links = await _fileRepository.GetLinksByFileIdAsync(fileId);

                _logger.LogInformation("Se obtuvieron {Count} links para el archivo {FileId} del usuario {UserId}", links.Count(), fileId, userId);
                return Ok(links);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al obtener los links del archivo {FileId}", fileId);
                return StatusCode(500, "Error interno del servidor al obtener los links del archivo");
            }
        }

        /// <summary>
        /// Obtiene la ruta de almacenamiento de archivos configurada
        /// </summary>
        /// <returns>Ruta absoluta donde almacenar los archivos</returns>
        private string GetUploadsPath()
        {
            // Prioridad 1: Verificar si estamos en un contenedor Docker
            var dockerSharedPath = "/app/shared";
            if (Directory.Exists(dockerSharedPath))
            {
                return dockerSharedPath;
            }

            // Prioridad 2: Intentar obtener la ruta desde configuración
            var configuredPath = _configuration["FileStorage:UploadPath"];

            if (!string.IsNullOrEmpty(configuredPath))
            {
                // Si es una ruta absoluta, usarla directamente
                if (Path.IsPathRooted(configuredPath))
                {
                    return configuredPath;
                }

                // Si es relativa, combinarla con el directorio base de la aplicación
                return Path.Combine(AppContext.BaseDirectory, configuredPath);
            }

            // Prioridad 3: Ruta por defecto para desarrollo local
            var projectDirectory = Directory.GetParent(AppContext.BaseDirectory)?.Parent?.Parent?.Parent?.FullName;
            if (projectDirectory != null)
            {
                var localSharedPath = Path.Combine(projectDirectory, "volumes", "shared_files");
                if (Directory.Exists(localSharedPath))
                {
                    return localSharedPath;
                }

                // Crear la carpeta si no existe (para desarrollo local)
                Directory.CreateDirectory(localSharedPath);
                return localSharedPath;
            }

            // Fallback: crear carpeta en el directorio de la aplicación
            return Path.Combine(AppContext.BaseDirectory, "uploads");
        }

        /// <summary>
        /// Envía una petición POST al servicio de procesamiento
        /// </summary>
        /// <param name="email">Email del usuario</param>
        /// <param name="fileId">ID del archivo a procesar</param>
        /// <returns>True si la petición fue exitosa, false en caso contrario</returns>
        private async Task<bool> SendProcessRequest(string email, int fileId)
        {
            try
            {
                // Obtener la URL del servicio de procesamiento desde variables de entorno o configuración
                var baseUrl = Environment.GetEnvironmentVariable("PROCESSING_SERVICE_BASE_URL") 
                            ?? _configuration["ProcessingService:BaseUrl"];
                var endpoint = Environment.GetEnvironmentVariable("PROCESSING_SERVICE_ENDPOINT") 
                             ?? _configuration["ProcessingService:ProcessEndpoint"];
                
                if (string.IsNullOrEmpty(baseUrl) || string.IsNullOrEmpty(endpoint))
                {
                    _logger.LogError("URL del servicio de procesamiento no configurada");
                    return false;
                }

                var processUrl = $"{baseUrl.TrimEnd('/')}{endpoint}";

                // Crear el payload para la petición
                var payload = new
                {
                    email = email,
                    file_id = fileId
                };

                var jsonContent = JsonSerializer.Serialize(payload);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                _logger.LogInformation("Enviando petición de procesamiento a {Url} para archivo {FileId} y usuario {Email}", 
                    processUrl, fileId, email);

                // Enviar la petición POST
                var response = await _httpClient.PostAsync(processUrl, content);

                if (response.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Petición de procesamiento enviada exitosamente para archivo {FileId}", fileId);
                    return true;
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogWarning("Error en la petición de procesamiento para archivo {FileId}. Status: {StatusCode}, Content: {Content}", 
                        fileId, response.StatusCode, errorContent);
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Excepción al enviar petición de procesamiento para archivo {FileId}", fileId);
                return false;
            }
        }
    }
}