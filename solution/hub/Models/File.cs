using System.ComponentModel.DataAnnotations;

namespace hub.Models
{
    public class File
    {
        public int Id { get; set; }
        
        [Required]
        public int TotalLinks { get; set; }
        
        [Required]
        [MaxLength(500)]
        public required string FilePath { get; set; }
        
        [Required]
        [MaxLength(255)]
        public required string FileName { get; set; }
        
        [Required]
        public int TotalProcessed { get; set; }
        
        [Required]
        public int TotalFailed { get; set; }
        
        [Required]
        [MaxLength(50)]
        public required string Status { get; set; }
        
        public DateTime UploadedAt { get; set; }
        
        [Required]
        public int UserId { get; set; }
        
        // Navigation property
        public User User { get; set; } = null!;
    }
}