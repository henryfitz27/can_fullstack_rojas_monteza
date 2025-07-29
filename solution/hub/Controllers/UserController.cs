using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using hub.Models;
using hub.Dtos;
using hub.Services;
using hub.Interfaces;
using BCrypt.Net;

namespace hub.Controllers
{
    [ApiController]
    [Route("")]
    public class UserController : ControllerBase
    {
        private readonly IUserRepository _userRepository;
        private readonly ILogger<UserController> _logger;
        private readonly IJwtService _jwtService;

        public UserController(IUserRepository userRepository, ILogger<UserController> logger, IJwtService jwtService)
        {
            _userRepository = userRepository;
            _logger = logger;
            _jwtService = jwtService;
        }

        /// <summary>
        /// Registra un nuevo usuario en el sistema
        /// </summary>
        /// <param name="registrationDto">Datos del usuario a registrar</param>
        /// <returns>Los datos del usuario registrado</returns>
        [HttpPost("register")]
        [AllowAnonymous]
        public async Task<ActionResult<UserResponseDto>> Register([FromBody] UserRegistrationDto registrationDto)
        {
            try
            {
                // Validar que el email no esté ya registrado
                var emailExists = await _userRepository.EmailExistsAsync(registrationDto.Email);
                if (emailExists)
                {
                    return BadRequest("El email ya está registrado en el sistema");
                }

                // Crear hash de la contraseña
                var hashedPassword = BCrypt.Net.BCrypt.HashPassword(registrationDto.Password);

                // Crear el nuevo usuario
                var user = new User
                {
                    FirstName = registrationDto.FirstName,
                    LastName = registrationDto.LastName,
                    Email = registrationDto.Email.ToLower(),
                    Password = hashedPassword,
                    CreatedAt = DateTime.UtcNow
                };

                var createdUser = await _userRepository.CreateAsync(user);

                // Crear respuesta sin incluir la contraseña
                var response = new UserResponseDto
                {
                    Id = createdUser.Id,
                    FirstName = createdUser.FirstName,
                    LastName = createdUser.LastName,
                    Email = createdUser.Email,
                    CreatedAt = createdUser.CreatedAt
                };

                _logger.LogInformation("Usuario registrado exitosamente con ID {UserId}", createdUser.Id);
                return CreatedAtAction(nameof(Register), new { id = createdUser.Id }, response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al registrar usuario con email {Email}", registrationDto.Email);
                return StatusCode(500, "Error interno del servidor al registrar usuario");
            }
        }

        /// <summary>
        /// Inicia sesión de un usuario y devuelve un JWT token
        /// </summary>
        /// <param name="loginDto">Credenciales de inicio de sesión</param>
        /// <returns>Token JWT y datos del usuario</returns>
        [HttpPost("login")]
        [AllowAnonymous]
        public async Task<ActionResult<LoginResponseDto>> Login([FromBody] UserLoginDto loginDto)
        {
            try
            {
                // Buscar usuario por email
                var user = await _userRepository.GetByEmailAsync(loginDto.Email);

                if (user == null)
                {
                    return BadRequest("Credenciales inválidas");
                }

                // Verificar contraseña
                if (!BCrypt.Net.BCrypt.Verify(loginDto.Password, user.Password))
                {
                    return BadRequest("Credenciales inválidas");
                }

                // Generar token JWT
                var token = _jwtService.GenerateToken(user);
                var expiresAt = DateTime.UtcNow.AddMinutes(60); // Debería coincidir con la configuración

                // Crear respuesta
                var response = new LoginResponseDto
                {
                    Token = token,
                    User = new UserResponseDto
                    {
                        Id = user.Id,
                        FirstName = user.FirstName,
                        LastName = user.LastName,
                        Email = user.Email,
                        CreatedAt = user.CreatedAt
                    },
                    ExpiresAt = expiresAt
                };

                _logger.LogInformation("Usuario {UserId} ha iniciado sesión exitosamente", user.Id);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error al intentar iniciar sesión con email {Email}", loginDto.Email);
                return StatusCode(500, "Error interno del servidor al iniciar sesión");
            }
        }
    }
}