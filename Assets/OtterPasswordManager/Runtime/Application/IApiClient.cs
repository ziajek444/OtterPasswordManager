using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using OtterPasswordManager.Application.Models;

namespace OtterPasswordManager.Application
{
    public interface IApiClient
    {
        Task<TokenPair> LoginAsync(
            string login,
            string password,
            CancellationToken cancellationToken = default);

        Task<User> RegisterAsync(
            string login,
            string password,
            CancellationToken cancellationToken = default);

        Task<IReadOnlyList<PasswordEntry>> GetPasswordsAsync(
            CancellationToken cancellationToken = default);

        Task<PasswordEntry> CreatePasswordAsync(
            PasswordEntryWrite entry,
            CancellationToken cancellationToken = default);

        Task<PasswordEntry> UpdatePasswordAsync(
            int id,
            PasswordEntryWrite entry,
            CancellationToken cancellationToken = default);

        Task DeletePasswordAsync(
            int id,
            CancellationToken cancellationToken = default);
    }
}
