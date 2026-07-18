using OtterPasswordManager.Application;
using OtterPasswordManager.Infrastructure.Api;
using OtterPasswordManager.Infrastructure.Authentication;

namespace OtterPasswordManager.Composition
{
    public static class ApiClientFactory
    {
        public static IApiClient Create(string baseUrl)
        {
            var transport = new UnityHttpTransport(baseUrl);
            var tokenStore = new InMemoryTokenStore();
            return new ApiClient(transport, tokenStore);
        }
    }
}
