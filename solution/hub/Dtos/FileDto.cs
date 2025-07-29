using System.ComponentModel.DataAnnotations;

namespace hub.Dtos
{
    public class FileResponseDto
    {
        public int Id { get; set; }
        public int TotalLinks { get; set; }
        public required string FilePath { get; set; }
        public required string FileName { get; set; }
        public int TotalProcessed { get; set; }
        public int TotalFailed { get; set; }
        public required string Status { get; set; }
        public DateTime UploadedAt { get; set; }
        public int UserId { get; set; }
    }

    public class FileUploadResponseDto
    {
        public int Id { get; set; }
        public required string FileName { get; set; }
        public required string Status { get; set; }
        public DateTime UploadedAt { get; set; }
        public string? Message { get; set; }
    }
}