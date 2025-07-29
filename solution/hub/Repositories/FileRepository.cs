using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Http;
using hub.Data;
using hub.Interfaces;
using hub.Dtos;
using FileModel = hub.Models.File;

namespace hub.Repositories
{
    public class FileRepository : IFileRepository
    {
        private readonly ApplicationDbContext _context;

        public FileRepository(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<FileResponseDto>> GetFilesByUserIdAsync(int userId)
        {
            return await _context.Files
                .Where(f => f.UserId == userId)
                .Select(f => new FileResponseDto
                {
                    Id = f.Id,
                    TotalLinks = f.TotalLinks,
                    FilePath = f.FilePath,
                    FileName = f.FileName,
                    TotalProcessed = f.TotalProcessed,
                    TotalFailed = f.TotalFailed,
                    Status = f.Status,
                    UploadedAt = f.UploadedAt,
                    UserId = f.UserId
                })
                .ToListAsync();
        }

        public async Task<FileModel> CreateFileAsync(FileModel file)
        {
            _context.Files.Add(file);
            await _context.SaveChangesAsync();
            return file;
        }

        public async Task<FileModel?> GetFileByIdAsync(int fileId)
        {
            return await _context.Files
                .FirstOrDefaultAsync(f => f.Id == fileId);
        }

        public async Task<FileModel?> GetFileByIdAndUserIdAsync(int fileId, int userId)
        {
            return await _context.Files
                .FirstOrDefaultAsync(f => f.Id == fileId && f.UserId == userId);
        }

        public async Task<bool> UpdateFileAsync(FileModel file)
        {
            try
            {
                _context.Files.Update(file);
                await _context.SaveChangesAsync();
                return true;
            }
            catch
            {
                return false;
            }
        }

        public async Task<bool> DeleteFileAsync(int fileId)
        {
            try
            {
                var file = await _context.Files.FindAsync(fileId);
                if (file != null)
                {
                    _context.Files.Remove(file);
                    await _context.SaveChangesAsync();
                    return true;
                }
                return false;
            }
            catch
            {
                return false;
            }
        }

        public async Task<string> SavePhysicalFileAsync(IFormFile file, int userId, string uploadsPath)
        {
            // Crear directorio si no existe
            if (!Directory.Exists(uploadsPath))
            {
                Directory.CreateDirectory(uploadsPath);
            }

            // Generar nombre único para el archivo
            var fileExtension = Path.GetExtension(file.FileName).ToLowerInvariant();
            var uniqueFileName = $"{userId}_{DateTime.UtcNow:yyyyMMdd_HHmmss}_{Guid.NewGuid():N}{fileExtension}";
            var filePath = Path.Combine(uploadsPath, uniqueFileName);

            // Guardar el archivo físicamente
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            return filePath;
        }

        public async Task<IEnumerable<LinkResponseDto>> GetLinksByFileIdAsync(int fileId)
        {
            return await _context.Links
                .Where(l => l.FileId == fileId)
                .Select(l => new LinkResponseDto
                {
                    Id = l.Id,
                    FileId = l.FileId,
                    Url = l.Url,
                    Title = l.Title,
                    PostDate = l.PostDate,
                    Content = l.Content,
                    PageExists = l.PageExists,
                    Success = l.Success,
                    ErrorDescription = l.ErrorDescription,
                    ProcessedDate = l.ProcessedDate
                })
                .ToListAsync();
        }
    }
}
