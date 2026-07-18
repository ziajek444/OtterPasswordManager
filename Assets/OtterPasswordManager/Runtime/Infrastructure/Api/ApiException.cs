using System;

namespace OtterPasswordManager.Infrastructure.Api
{
    public sealed class ApiException : Exception
    {
        public ApiException(long statusCode, string message, string responseBody)
            : base(message)
        {
            StatusCode = statusCode;
            ResponseBody = responseBody;
        }

        public long StatusCode { get; }
        public string ResponseBody { get; }
    }
}
