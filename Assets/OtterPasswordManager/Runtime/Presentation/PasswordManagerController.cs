using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using OtterPasswordManager.Application;
using OtterPasswordManager.Application.Models;
using OtterPasswordManager.Infrastructure.Api;
using OtterPasswordManager.Infrastructure.Authentication;
using UnityEngine;
using UnityEngine.UI;

namespace OtterPasswordManager.Presentation
{
    public sealed class PasswordManagerController : MonoBehaviour
    {
        private IApiClient _apiClient;
        private ITokenStore _tokenStore;
        private Canvas _canvas;
        private RectTransform _viewRoot;
        private CancellationTokenSource _lifetime;
        private bool _busy;

        public void Initialize(IApiClient apiClient, ITokenStore tokenStore)
        {
            _apiClient = apiClient;
            _tokenStore = tokenStore;
            _lifetime = new CancellationTokenSource();
            _canvas = UiFactory.CreateCanvas(transform);
            _viewRoot = UiFactory.CreateViewRoot(_canvas.transform);
            ShowLogin();
        }

        private void OnDestroy()
        {
            if (_lifetime == null)
                return;
            _lifetime.Cancel();
            _lifetime.Dispose();
        }

        private void ShowLogin(string initialMessage = null)
        {
            UiFactory.Clear(_viewRoot);
            RectTransform panel = UiFactory.CreateCenteredPanel(_viewRoot, 460f);
            Text title = UiFactory.CreateText(
                "Title", panel, "Otter Password Manager", 30, TextAnchor.MiddleCenter);
            title.fontStyle = FontStyle.Bold;
            UiFactory.CreateText(
                "Subtitle", panel, "Zaloguj się do swojego sejfu", 17, TextAnchor.MiddleCenter);
            InputField login = UiFactory.CreateInput("Login", panel, "Login");
            InputField password = UiFactory.CreateInput("Password", panel, "Hasło", true);
            Text status = UiFactory.CreateText(
                "Status", panel, initialMessage ?? string.Empty, 15, TextAnchor.MiddleCenter);
            Button submit = UiFactory.CreateButton("Login button", panel, "Zaloguj");
            Button register = UiFactory.CreateButton("Register link", panel, "Utwórz konto", Color.gray);

            submit.onClick.AddListener(() => RunActionAsync(
                async () =>
                {
                    await _apiClient.LoginAsync(login.text, password.text, _lifetime.Token);
                    await ShowVaultAsync();
                }, status, submit));
            register.onClick.AddListener(ShowRegister);
        }

        private void ShowRegister()
        {
            UiFactory.Clear(_viewRoot);
            RectTransform panel = UiFactory.CreateCenteredPanel(_viewRoot, 460f);
            Text title = UiFactory.CreateText(
                "Title", panel, "Utwórz konto", 30, TextAnchor.MiddleCenter);
            title.fontStyle = FontStyle.Bold;
            InputField login = UiFactory.CreateInput("Login", panel, "Login (min. 3 znaki)");
            InputField password = UiFactory.CreateInput("Password", panel, "Hasło (min. 12 znaków)", true);
            Text status = UiFactory.CreateText("Status", panel, string.Empty, 15, TextAnchor.MiddleCenter);
            Button submit = UiFactory.CreateButton("Register button", panel, "Zarejestruj");
            Button back = UiFactory.CreateButton("Back", panel, "Wróć do logowania", Color.gray);

            submit.onClick.AddListener(() => RunActionAsync(
                async () =>
                {
                    await _apiClient.RegisterAsync(login.text, password.text, _lifetime.Token);
                    await _apiClient.LoginAsync(login.text, password.text, _lifetime.Token);
                    await ShowVaultAsync();
                }, status, submit));
            back.onClick.AddListener(() => ShowLogin());
        }

        private async Task ShowVaultAsync()
        {
            UiFactory.Clear(_viewRoot);
            RectTransform root = UiFactory.CreateFullPanel(_viewRoot);
            var layout = root.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 14f;
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;

            RectTransform header = UiFactory.CreateHorizontalRow(root);
            Text title = UiFactory.CreateText("Title", header, "Twój sejf", 30);
            title.fontStyle = FontStyle.Bold;
            Button add = UiFactory.CreateButton("Add", header, "+ Dodaj hasło");
            Button logout = UiFactory.CreateButton("Logout", header, "Wyloguj", Color.gray);
            Text status = UiFactory.CreateText("Status", root, "Ładowanie…", 15);
            ScrollRect scroll = UiFactory.CreateScrollView(root);
            var scrollLayout = scroll.gameObject.AddComponent<LayoutElement>();
            scrollLayout.flexibleHeight = 1f;

            add.onClick.AddListener(() => ShowEntryEditor(null));
            logout.onClick.AddListener(() =>
            {
                _tokenStore.Clear();
                ShowLogin("Wylogowano.");
            });

            try
            {
                IReadOnlyList<PasswordEntry> entries =
                    await _apiClient.GetPasswordsAsync(_lifetime.Token);
                status.text = entries.Count == 0
                    ? "Sejf jest pusty. Dodaj pierwszy wpis."
                    : entries.Count + " zapisanych wpisów";
                foreach (PasswordEntry entry in entries)
                    CreatePasswordCard(scroll.content, entry, status);
            }
            catch (Exception exception)
            {
                status.text = GetErrorMessage(exception);
            }
        }

        private void CreatePasswordCard(Transform parent, PasswordEntry entry, Text status)
        {
            RectTransform card = UiFactory.CreateCard(parent);
            Text name = UiFactory.CreateText("Service", card, entry.ServiceName, 22);
            name.fontStyle = FontStyle.Bold;
            UiFactory.CreateText("Username", card, "Login: " + entry.Username, 16);
            UiFactory.CreateText("Password", card, "Hasło: " + entry.Password, 16);
            if (!string.IsNullOrWhiteSpace(entry.Website))
                UiFactory.CreateText("Website", card, "WWW: " + entry.Website, 15);
            if (!string.IsNullOrWhiteSpace(entry.Notes))
                UiFactory.CreateText("Notes", card, entry.Notes, 15);

            RectTransform buttons = UiFactory.CreateHorizontalRow(card);
            Button edit = UiFactory.CreateButton("Edit", buttons, "Edytuj", Color.gray);
            Button delete = UiFactory.CreateDangerButton("Delete", buttons, "Usuń");
            edit.onClick.AddListener(() => ShowEntryEditor(entry));
            delete.onClick.AddListener(() => RunActionAsync(
                async () =>
                {
                    await _apiClient.DeletePasswordAsync(entry.Id, _lifetime.Token);
                    await ShowVaultAsync();
                }, status, delete));
        }

        private void ShowEntryEditor(PasswordEntry existing)
        {
            UiFactory.Clear(_viewRoot);
            RectTransform panel = UiFactory.CreateCenteredPanel(_viewRoot, 600f);
            Text title = UiFactory.CreateText(
                "Title",
                panel,
                existing == null ? "Nowe hasło" : "Edytuj hasło",
                28,
                TextAnchor.MiddleCenter);
            title.fontStyle = FontStyle.Bold;

            InputField serviceName = UiFactory.CreateInput("Service", panel, "Nazwa usługi");
            InputField username = UiFactory.CreateInput("Username", panel, "Login / e-mail");
            InputField password = UiFactory.CreateInput("Password", panel, "Hasło", true);
            InputField website = UiFactory.CreateInput("Website", panel, "Adres strony (opcjonalnie)");
            InputField notes = UiFactory.CreateInput("Notes", panel, "Notatki (opcjonalnie)", false, true);
            if (existing != null)
            {
                serviceName.text = existing.ServiceName;
                username.text = existing.Username;
                password.text = existing.Password;
                website.text = existing.Website ?? string.Empty;
                notes.text = existing.Notes ?? string.Empty;
            }

            Text status = UiFactory.CreateText("Status", panel, string.Empty, 15, TextAnchor.MiddleCenter);
            RectTransform buttons = UiFactory.CreateHorizontalRow(panel);
            Button save = UiFactory.CreateButton("Save", buttons, "Zapisz");
            Button cancel = UiFactory.CreateButton("Cancel", buttons, "Anuluj", Color.gray);

            save.onClick.AddListener(() => RunActionAsync(
                async () =>
                {
                    var payload = new PasswordEntryWrite
                    {
                        ServiceName = serviceName.text,
                        Username = username.text,
                        Password = password.text,
                        Website = EmptyToNull(website.text),
                        Notes = EmptyToNull(notes.text)
                    };
                    if (existing == null)
                        await _apiClient.CreatePasswordAsync(payload, _lifetime.Token);
                    else
                        await _apiClient.UpdatePasswordAsync(existing.Id, payload, _lifetime.Token);
                    await ShowVaultAsync();
                }, status, save));
            cancel.onClick.AddListener(() => RunActionAsync(ShowVaultAsync, status, cancel));
        }

        private async void RunActionAsync(Func<Task> action, Text status, Button button)
        {
            if (_busy)
                return;
            _busy = true;
            button.interactable = false;
            status.text = "Proszę czekać…";
            try
            {
                await action();
            }
            catch (OperationCanceledException)
            {
                status.text = "Operacja anulowana.";
            }
            catch (Exception exception)
            {
                status.text = GetErrorMessage(exception);
            }
            finally
            {
                _busy = false;
                if (button != null)
                    button.interactable = true;
            }
        }

        private static string GetErrorMessage(Exception exception)
        {
            var apiException = exception as ApiException;
            if (apiException != null)
            {
                if (apiException.StatusCode == 0)
                    return "Nie można połączyć się z serwerem. Uruchom backend FastAPI.";
                return "Błąd API " + apiException.StatusCode + ": " + apiException.ResponseBody;
            }
            return "Błąd: " + exception.Message;
        }

        private static string EmptyToNull(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
        }
    }
}
