using OtterPasswordManager.Application.Models;

namespace OtterPasswordManager.Infrastructure.Authentication
{
    public interface ITokenStore
    {
        string AccessToken { get; }
        string RefreshToken { get; }
        void Save(TokenPair tokens);
        void Clear();
    }
}
