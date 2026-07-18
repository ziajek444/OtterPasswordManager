using OtterPasswordManager.Application.Models;

namespace OtterPasswordManager.Infrastructure.Authentication
{
    public sealed class InMemoryTokenStore : ITokenStore
    {
        public string AccessToken { get; private set; }
        public string RefreshToken { get; private set; }

        public void Save(TokenPair tokens)
        {
            AccessToken = tokens.AccessToken;
            RefreshToken = tokens.RefreshToken;
        }

        public void Clear()
        {
            AccessToken = null;
            RefreshToken = null;
        }
    }
}
