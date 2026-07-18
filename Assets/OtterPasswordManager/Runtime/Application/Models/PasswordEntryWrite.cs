using Newtonsoft.Json;

namespace OtterPasswordManager.Application.Models
{
    public sealed class PasswordEntryWrite
    {
        [JsonProperty("service_name")]
        public string ServiceName { get; set; }

        [JsonProperty("username")]
        public string Username { get; set; }

        [JsonProperty("password")]
        public string Password { get; set; }

        [JsonProperty("website")]
        public string Website { get; set; }

        [JsonProperty("notes")]
        public string Notes { get; set; }
    }
}
