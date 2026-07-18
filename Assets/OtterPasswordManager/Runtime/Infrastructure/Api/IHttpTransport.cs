using System.Threading;
using System.Threading.Tasks;

namespace OtterPasswordManager.Infrastructure.Api
{
    public interface IHttpTransport
    {
        Task<TResponse> SendAsync<TResponse>(
            string method,
            string path,
            object body,
            string bearerToken,
            CancellationToken cancellationToken = default);

        Task SendAsync(
            string method,
            string path,
            object body,
            string bearerToken,
            CancellationToken cancellationToken = default);
    }
}
