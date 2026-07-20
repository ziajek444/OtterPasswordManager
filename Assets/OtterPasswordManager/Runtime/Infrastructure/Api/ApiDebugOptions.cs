namespace OtterPasswordManager.Infrastructure.Api
{
    public sealed class ApiDebugOptions
    {
        public ApiDebugOptions(bool enabled)
        {
            Enabled = enabled;
        }

        public bool Enabled { get; }
    }
}
