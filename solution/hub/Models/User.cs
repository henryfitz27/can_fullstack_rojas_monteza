using System.ComponentModel.DataAnnotations;

namespace hub.Models
{
    public class User
    {
        public int Id { get; set; }
        
        [Required]
        [MaxLength(100)]
        public required string FirstName { get; set; }
        
        [Required]
        [MaxLength(100)]
        public required string LastName { get; set; }
        
        [Required]
        [EmailAddress]
        [MaxLength(255)]
        public required string Email { get; set; }
        
        [Required]
        public required string Password { get; set; }
        
        [MaxLength(20)]
        public string? PhoneNumber { get; set; }
        
        public DateTime CreatedAt { get; set; }
      
    }
}