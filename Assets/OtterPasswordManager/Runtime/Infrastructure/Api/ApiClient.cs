using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using OtterPasswordManager.Application;
using OtterPasswordManager.Application.Models;
using OtterPasswordManager.Infrastructure.Api.Requests;
using OtterPasswordManager.Infrastructure.Authentication;
using UnityEngine.Networking;

namespace OtterPasswordManager.Infrastructure.Api
{
    public sealed class ApiClient : IApiClient
    {
        private readonly IHttpTransport _transport;
        private readonly ITokenStore _tokenStore;

        public ApiClient(IHttpTransport transport, ITokenStore tokenStore)
        {
            _transport = transport ?? throw new ArgumentNullException(nameof(transport));
            _tokenStore = tokenStore ?? throw new ArgumentNullException(nameof(tokenStore));
        }

        public async Task<TokenPair> LoginAsync(
            string login,
            string password,
            CancellationToken cancellationToken = default)
        {
            TokenPair tokens = await _transport.SendAsync<TokenPair>(
                UnityWebRequest.kHttpVerbPOST,
                "/login",
                new LoginRequest(login, password),
                null,
                cancellationToken);
            _tokenStore.Save(tokens);
            return tokens;
        }

        public Task<User> RegisterAsync(
            string login,
            string password,
            CancellationToken cancellationToken = default)
        {
            return _transport.SendAsync<User>(
                UnityWebRequest.kHttpVerbPOST,
                "/register",
                new RegisterRequest(login, password),
                null,
                cancellationToken);
        }

        public async Task<IReadOnlyList<PasswordEntry>> GetPasswordsAsync(
            CancellationToken cancellationToken = default)
        {
            List<PasswordEntry> entries = await _transport.SendAsync<List<PasswordEntry>>(
                UnityWebRequest.kHttpVerbGET,
                "/passwords",
                null,
                RequireAccessToken(),
                cancellationToken);
            return entries;
        }

        public Task<PasswordEntry> CreatePasswordAsync(
            PasswordEntryWrite entry,
            CancellationToken cancellationToken = default)
        {
            if (entry == null)
                throw new ArgumentNullException(nameof(entry));

            return _transport.SendAsync<PasswordEntry>(
                UnityWebRequest.kHttpVerbPOST,
                "/passwords",
                entry,
                RequireAccessToken(),
                cancellationToken);
        }

        public Task<PasswordEntry> UpdatePasswordAsync(
            int id,
            PasswordEntryWrite entry,
            CancellationToken cancellationToken = default)
        {
            if (id <= 0)
                throw new ArgumentOutOfRangeException(nameof(id));
            if (entry == null)
                throw new ArgumentNullException(nameof(entry));

            return _transport.SendAsync<PasswordEntry>(
                UnityWebRequest.kHttpVerbPUT,
                "/passwords/" + id,
                entry,
                RequireAccessToken(),
                cancellationToken);
        }

        public Task DeletePasswordAsync(
            int id,
            CancellationToken cancellationToken = default)
        {
            if (id <= 0)
                throw new ArgumentOutOfRangeException(nameof(id));

            return _transport.SendAsync(
                UnityWebRequest.kHttpVerbDELETE,
                "/passwords/" + id,
                null,
                RequireAccessToken(),
                cancellationToken);
        }

        private string RequireAccessToken()
        {
            if (string.IsNullOrEmpty(_tokenStore.AccessToken))
                throw new InvalidOperationException("Login is required before accessing passwords.");

            return _tokenStore.AccessToken;
        }
    }
}
