using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UnityEngine.Networking;

namespace OtterPasswordManager.Infrastructure.Api
{
    public sealed class UnityHttpTransport : IHttpTransport
    {
        private const string JsonContentType = "application/json";
        private readonly string _baseUrl;
        private readonly JsonSerializerSettings _serializerSettings;

        public UnityHttpTransport(string baseUrl)
        {
            if (string.IsNullOrWhiteSpace(baseUrl))
                throw new ArgumentException("API base URL is required.", nameof(baseUrl));

            _baseUrl = baseUrl.TrimEnd('/');
            _serializerSettings = new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Include
            };
        }

        public async Task<TResponse> SendAsync<TResponse>(
            string method,
            string path,
            object body,
            string bearerToken,
            CancellationToken cancellationToken = default)
        {
            string responseBody = await SendInternalAsync(
                method, path, body, bearerToken, cancellationToken);
            return JsonConvert.DeserializeObject<TResponse>(responseBody, _serializerSettings);
        }

        public async Task SendAsync(
            string method,
            string path,
            object body,
            string bearerToken,
            CancellationToken cancellationToken = default)
        {
            await SendInternalAsync(method, path, body, bearerToken, cancellationToken);
        }

        private async Task<string> SendInternalAsync(
            string method,
            string path,
            object body,
            string bearerToken,
            CancellationToken cancellationToken)
        {
            using (UnityWebRequest request = CreateRequest(method, path, body, bearerToken))
            {
                await SendAsync(request, cancellationToken);
                string responseBody = request.downloadHandler != null
                    ? request.downloadHandler.text
                    : string.Empty;

                if (request.result != UnityWebRequest.Result.Success)
                    throw CreateException(request, responseBody);

                return responseBody;
            }
        }

        private UnityWebRequest CreateRequest(
            string method,
            string path,
            object body,
            string bearerToken)
        {
            var request = new UnityWebRequest(_baseUrl + NormalizePath(path), method)
            {
                downloadHandler = new DownloadHandlerBuffer()
            };

            if (body != null)
            {
                string json = JsonConvert.SerializeObject(body, _serializerSettings);
                request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(json));
                request.SetRequestHeader("Content-Type", JsonContentType);
            }

            request.SetRequestHeader("Accept", JsonContentType);
            if (!string.IsNullOrEmpty(bearerToken))
                request.SetRequestHeader("Authorization", "Bearer " + bearerToken);

            return request;
        }

        private static async Task SendAsync(
            UnityWebRequest request,
            CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            UnityWebRequestAsyncOperation operation = request.SendWebRequest();
            var completion = new TaskCompletionSource<bool>(
                TaskCreationOptions.RunContinuationsAsynchronously);

            operation.completed += _ => completion.TrySetResult(true);
            if (operation.isDone)
                completion.TrySetResult(true);
            using (cancellationToken.Register(() => completion.TrySetCanceled()))
                await completion.Task;
        }

        private static ApiException CreateException(UnityWebRequest request, string responseBody)
        {
            string message = string.IsNullOrEmpty(request.error)
                ? "The API request failed."
                : request.error;
            return new ApiException(request.responseCode, message, responseBody);
        }

        private static string NormalizePath(string path)
        {
            return path.StartsWith("/", StringComparison.Ordinal) ? path : "/" + path;
        }
    }
}
