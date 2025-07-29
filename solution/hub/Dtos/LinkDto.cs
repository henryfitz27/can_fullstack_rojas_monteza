using System.ComponentModel.DataAnnotations;

namespace hubs.Dtos
{
    public class LinkResponseDto
    {
        public int Id { get; set; }
        public int FileId { get; set; }
        public required string Url { get; set; }
        public string? Title { get; set; }
        public DateTime? PostDate { get; set; }
        public string? Content { get; set; }
        public bool PageExists { get; set; }
        public bool Success { get; set; }
        public string? ErrorDescription { get; set; }
        public DateTime? ProcessedDate { get; set; }
    }

    public class LinkCreateDto
    {
        [Required]
        public int FileId { get; set; }
        
        [Required]
        [MaxLength(2000)]
        public required string Url { get; set; }
        
        [MaxLength(500)]
        public string? Title { get; set; }
        
        public DateTime? PostDate { get; set; }
        
        public string? Content { get; set; }
        
        public bool PageExists { get; set; } = false;
        
        public bool Success { get; set; } = false;
        
        [MaxLength(1000)]
        public string? ErrorDescription { get; set; }
        
        public DateTime? ProcessedDate { get; set; }
    }

    public class LinkUpdateDto
    {
        [MaxLength(500)]
        public string? Title { get; set; }
        
        public DateTime? PostDate { get; set; }
        
        public string? Content { get; set; }
        
        public bool? PageExists { get; set; }
        
        public bool? Success { get; set; }
        
        [MaxLength(1000)]
        public string? ErrorDescription { get; set; }
        
        public DateTime? ProcessedDate { get; set; }
    }
}