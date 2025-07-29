using System.ComponentModel.DataAnnotations;

namespace hub.Models
{
    public class Link
    {
        public int Id { get; set; }
        
        [Required]
        public int FileId { get; set; }
        
        [Required]
        [MaxLength(2000)]
        public required string Url { get; set; }
        
        [MaxLength(500)]
        public string? Title { get; set; }
        
        public DateTime? PostDate { get; set; }
        
        public string? Content { get; set; }
        
        [Required]
        public bool PageExists { get; set; }
        
        [Required]
        public bool Success { get; set; }
        
        [MaxLength(1000)]
        public string? ErrorDescription { get; set; }
        
        public DateTime? ProcessedDate { get; set; }
        
        // Navigation property
        public File File { get; set; } = null!;
    }
}