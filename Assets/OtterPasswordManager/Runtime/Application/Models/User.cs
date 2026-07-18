using System;
using Newtonsoft.Json;

namespace OtterPasswordManager.Application.Models
{
    public sealed class User
    {
        [JsonProperty("id")]
        public int Id { get; set; }

        [JsonProperty("login")]
        public string Login { get; set; }

        [JsonProperty("created_at")]
        public DateTimeOffset CreatedAt { get; set; }
    }
}
