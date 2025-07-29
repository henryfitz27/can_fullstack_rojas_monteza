using hub.Dtos;
using Microsoft.AspNetCore.Http;
using FileModel = hub.Models.File;

namespace hub.Interfaces
{
    public interface IFileRepository
    {
        Task<IEnumerable<FileResponseDto>> GetFilesByUserIdAsync(int userId);
        Task<FileModel> CreateFileAsync(FileModel file);
        Task<FileModel?> GetFileByIdAsync(int fileId);
        Task<FileModel?> GetFileByIdAndUserIdAsync(int fileId, int userId);
        Task<bool> UpdateFileAsync(FileModel file);
        Task<bool> DeleteFileAsync(int fileId);
        Task<string> SavePhysicalFileAsync(IFormFile file, int userId, string uploadsPath);
        Task<IEnumerable<LinkResponseDto>> GetLinksByFileIdAsync(int fileId);
    }
}
