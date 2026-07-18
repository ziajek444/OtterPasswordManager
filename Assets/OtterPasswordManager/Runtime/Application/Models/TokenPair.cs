using Newtonsoft.Json;

namespace OtterPasswordManager.Application.Models
{
    public sealed class TokenPair
    {
        [JsonProperty("access_token")]
        public string AccessToken { get; set; }

        [JsonProperty("refresh_token")]
        public string RefreshToken { get; set; }

        [JsonProperty("token_type")]
        public string TokenType { get; set; }
    }
}
