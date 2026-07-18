using OtterPasswordManager.Application;
using OtterPasswordManager.Infrastructure.Api;
using OtterPasswordManager.Infrastructure.Authentication;
using OtterPasswordManager.Presentation;
using UnityEngine;

namespace OtterPasswordManager.Composition
{
    public static class ApplicationBootstrapper
    {
        private const string LocalApiUrl = "http://127.0.0.1:8000";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Initialize()
        {
            if (Object.FindObjectOfType<PasswordManagerController>() != null)
                return;

            var applicationObject = new GameObject("Otter Password Manager");
            Object.DontDestroyOnLoad(applicationObject);

            ITokenStore tokenStore = new InMemoryTokenStore();
            IHttpTransport transport = new UnityHttpTransport(LocalApiUrl);
            IApiClient apiClient = new ApiClient(transport, tokenStore);

            PasswordManagerController controller =
                applicationObject.AddComponent<PasswordManagerController>();
            controller.Initialize(apiClient, tokenStore);
        }
    }
}
