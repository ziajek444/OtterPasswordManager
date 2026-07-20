using System;
using System.Diagnostics;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Networking;

namespace OtterPasswordManager.Infrastructure.Api
{
    public sealed class UnityHttpTransport : IHttpTransport
    {
        private const string JsonContentType = "application/json";
        private readonly string _baseUrl;
        private readonly ApiDebugOptions _debugOptions;
        private readonly JsonSerializerSettings _serializerSettings;

        private static bool makeRedactedSensetiveData = false;

        public UnityHttpTransport(string baseUrl, ApiDebugOptions debugOptions = null)
        {
            if (string.IsNullOrWhiteSpace(baseUrl))
                throw new ArgumentException("API base URL is required.", nameof(baseUrl));

            _baseUrl = baseUrl.TrimEnd('/');
            _debugOptions = debugOptions ?? new ApiDebugOptions(false);
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
                LogRequest(request, bearerToken);
                Stopwatch stopwatch = Stopwatch.StartNew();
                await SendAsync(request, cancellationToken);
                stopwatch.Stop();
                string responseBody = request.downloadHandler != null
                    ? request.downloadHandler.text
                    : string.Empty;
                LogResponse(request, responseBody, stopwatch.ElapsedMilliseconds);

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

        private void LogRequest(UnityWebRequest request, string bearerToken)
        {
            if (!_debugOptions.Enabled)
                return;

            string requestBody = request.uploadHandler != null
                ? Encoding.UTF8.GetString(request.uploadHandler.data)
                : string.Empty;
            string authorization = string.IsNullOrEmpty(bearerToken)
                ? "none" :
                makeRedactedSensetiveData ? bearerToken : "Bearer [REDACTED]";

            UnityEngine.Debug.Log(
                "[API] --> " + request.method + " " + request.url + "\n" +
                "Authorization: " + authorization + "\n" +
                "Body: " + FormatRedactedJson(requestBody) + 
                "\nEND\n");
        }

        private void LogResponse(
            UnityWebRequest request,
            string responseBody,
            long elapsedMilliseconds)
        {
            if (!_debugOptions.Enabled)
                return;

            UnityEngine.Debug.Log(
                "[API] <-- " + request.responseCode + " " + request.method + " " +
                request.url + " (" + elapsedMilliseconds + " ms)\n" +
                "Body: " + FormatRedactedJson(responseBody) + 
                "\nEND\n");
        }

        private static string FormatRedactedJson(string json)
        {
            if (string.IsNullOrWhiteSpace(json))
                return "<empty>";

            try
            {
                JToken token = JToken.Parse(json);
                RedactSensitiveValues(token);
                return token.ToString(Formatting.Indented);
            }
            catch (JsonException)
            {
                return "<non-JSON body omitted>";
            }
        }

        private static void RedactSensitiveValues(JToken token)
        {
            var jsonObject = token as JObject;
            if (jsonObject != null)
            {
                foreach (JProperty property in jsonObject.Properties())
                {
                    if (IsSensitiveProperty(property.Name) && makeRedactedSensetiveData == true)
                        property.Value = "[REDACTED]";
                    else
                        RedactSensitiveValues(property.Value);
                }
                return;
            }

            var jsonArray = token as JArray;
            if (jsonArray == null)
                return;
            foreach (JToken item in jsonArray)
                RedactSensitiveValues(item);
        }

        private static bool IsSensitiveProperty(string propertyName)
        {
            return string.Equals(propertyName, "password", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "encrypted_password", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "hashed_password", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "access_token", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "refresh_token", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "jwt_secret", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(propertyName, "encryption_key", StringComparison.OrdinalIgnoreCase);
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
