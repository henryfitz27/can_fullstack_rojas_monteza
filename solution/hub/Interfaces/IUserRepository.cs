using hub.Models;

namespace hub.Interfaces
{
    public interface IUserRepository
    {
        Task<User?> GetByEmailAsync(string email);
        Task<User> CreateAsync(User user);
        Task<bool> EmailExistsAsync(string email);
    }
}
