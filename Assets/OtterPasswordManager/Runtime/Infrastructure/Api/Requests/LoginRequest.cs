using Newtonsoft.Json;

namespace OtterPasswordManager.Infrastructure.Api.Requests
{
    internal sealed class LoginRequest
    {
        public LoginRequest(string login, string password)
        {
            Login = login;
            Password = password;
        }

        [JsonProperty("login")]
        public string Login { get; private set; }

        [JsonProperty("password")]
        public string Password { get; private set; }
    }
}
