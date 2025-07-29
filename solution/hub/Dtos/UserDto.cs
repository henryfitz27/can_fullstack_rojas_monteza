using System.ComponentModel.DataAnnotations;

namespace hub.Dtos
{
    public class UserRegistrationDto
    {
        [Required(ErrorMessage = "El nombre es requerido")]
        [MaxLength(100, ErrorMessage = "El nombre no puede exceder 100 caracteres")]
        public required string FirstName { get; set; }
        
        [Required(ErrorMessage = "El apellido es requerido")]
        [MaxLength(100, ErrorMessage = "El apellido no puede exceder 100 caracteres")]
        public required string LastName { get; set; }
        
        [Required(ErrorMessage = "El email es requerido")]
        [EmailAddress(ErrorMessage = "Formato de email inválido")]
        [MaxLength(255, ErrorMessage = "El email no puede exceder 255 caracteres")]
        public required string Email { get; set; }
        
        [Required(ErrorMessage = "La contraseña es requerida")]
        [MinLength(6, ErrorMessage = "La contraseña debe tener al menos 6 caracteres")]
        public required string Password { get; set; }
    }
    
    public class UserLoginDto
    {
        [Required(ErrorMessage = "El email es requerido")]
        [EmailAddress(ErrorMessage = "Formato de email inválido")]
        public required string Email { get; set; }
        
        [Required(ErrorMessage = "La contraseña es requerida")]
        public required string Password { get; set; }
    }
    
    public class UserResponseDto
    {
        public int Id { get; set; }
        public required string FirstName { get; set; }
        public required string LastName { get; set; }
        public required string Email { get; set; }
        public DateTime CreatedAt { get; set; }
    }
    
    public class LoginResponseDto
    {
        public required string Token { get; set; }
        public required UserResponseDto User { get; set; }
        public DateTime ExpiresAt { get; set; }
    }
}