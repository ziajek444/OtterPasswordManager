using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace OtterPasswordManager.Presentation
{
    internal static class UiFactory
    {
        private static readonly Color Background = new Color32(19, 26, 39, 255);
        private static readonly Color Surface = new Color32(31, 41, 55, 255);
        private static readonly Color Primary = new Color32(45, 212, 191, 255);
        private static readonly Color Danger = new Color32(239, 68, 68, 255);
        private static readonly Color TextColor = new Color32(243, 244, 246, 255);
        private static readonly Color MutedText = new Color32(156, 163, 175, 255);
        private static Font _font;

        public static Canvas CreateCanvas(Transform parent)
        {
            EnsureEventSystem();
            GameObject canvasObject = CreateObject("Canvas", parent);
            var canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObject.AddComponent<GraphicRaycaster>();
            var scaler = canvasObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280f, 720f);
            scaler.matchWidthOrHeight = 0.5f;

            Image background = CreateImage("Background", canvasObject.transform, Background);
            Stretch(background.rectTransform);
            return canvas;
        }

        public static RectTransform CreateCenteredPanel(Transform parent, float width)
        {
            Image image = CreateImage("Panel", parent, Surface);
            RectTransform rect = image.rectTransform;
            rect.anchorMin = new Vector2(0.5f, 0.5f);
            rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(width, 0f);

            var layout = image.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(32, 32, 28, 28);
            layout.spacing = 14f;
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;
            image.gameObject.AddComponent<ContentSizeFitter>().verticalFit =
                ContentSizeFitter.FitMode.PreferredSize;
            return rect;
        }

        public static RectTransform CreateFullPanel(Transform parent)
        {
            Image image = CreateImage("Content", parent, new Color(0f, 0f, 0f, 0f));
            RectTransform rect = image.rectTransform;
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = new Vector2(48f, 32f);
            rect.offsetMax = new Vector2(-48f, -32f);
            return rect;
        }

        public static RectTransform CreateViewRoot(Transform parent)
        {
            Image image = CreateImage("Views", parent, new Color(0f, 0f, 0f, 0f));
            Stretch(image.rectTransform);
            return image.rectTransform;
        }

        public static Text CreateText(
            string name,
            Transform parent,
            string value,
            int size = 20,
            TextAnchor alignment = TextAnchor.MiddleLeft,
            Color? color = null)
        {
            GameObject textObject = CreateObject(name, parent);
            var text = textObject.AddComponent<Text>();
            text.font = Font;
            text.fontSize = size;
            text.text = value;
            text.color = color ?? TextColor;
            text.alignment = alignment;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            AddLayout(textObject, 34f);
            return text;
        }

        public static InputField CreateInput(
            string name,
            Transform parent,
            string placeholder,
            bool password = false,
            bool multiline = false)
        {
            Image background = CreateImage(name, parent, new Color32(17, 24, 39, 255));
            AddLayout(background.gameObject, multiline ? 96f : 48f);

            Text inputText = CreateText("Text", background.transform, string.Empty, 18);
            Stretch(inputText.rectTransform, 14f, 14f, 8f, 8f);
            inputText.supportRichText = false;

            Text placeholderText = CreateText(
                "Placeholder", background.transform, placeholder, 18, TextAnchor.MiddleLeft, MutedText);
            Stretch(placeholderText.rectTransform, 14f, 14f, 8f, 8f);

            var input = background.gameObject.AddComponent<InputField>();
            input.textComponent = inputText;
            input.placeholder = placeholderText;
            input.lineType = multiline
                ? InputField.LineType.MultiLineNewline
                : InputField.LineType.SingleLine;
            input.contentType = password
                ? InputField.ContentType.Password
                : InputField.ContentType.Standard;
            return input;
        }

        public static Button CreateButton(
            string name,
            Transform parent,
            string label,
            Color? color = null)
        {
            Image image = CreateImage(name, parent, color ?? Primary);
            AddLayout(image.gameObject, 46f);
            var button = image.gameObject.AddComponent<Button>();
            button.targetGraphic = image;
            ColorBlock colors = button.colors;
            colors.highlightedColor = Color.Lerp(image.color, Color.white, 0.15f);
            colors.pressedColor = Color.Lerp(image.color, Color.black, 0.15f);
            button.colors = colors;

            Text text = CreateText("Label", image.transform, label, 18, TextAnchor.MiddleCenter, Background);
            text.fontStyle = FontStyle.Bold;
            Stretch(text.rectTransform);
            return button;
        }

        public static Button CreateDangerButton(string name, Transform parent, string label)
        {
            return CreateButton(name, parent, label, Danger);
        }

        public static RectTransform CreateHorizontalRow(Transform parent, float spacing = 10f)
        {
            GameObject row = CreateObject("Row", parent);
            var layout = row.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = spacing;
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;
            row.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            return row.GetComponent<RectTransform>();
        }

        public static ScrollRect CreateScrollView(Transform parent)
        {
            Image viewport = CreateImage("Password list", parent, new Color(0f, 0f, 0f, 0f));
            viewport.gameObject.AddComponent<RectMask2D>();
            var scroll = viewport.gameObject.AddComponent<ScrollRect>();
            scroll.horizontal = false;

            GameObject contentObject = CreateObject("Content", viewport.transform);
            RectTransform content = contentObject.GetComponent<RectTransform>();
            content.anchorMin = new Vector2(0f, 1f);
            content.anchorMax = new Vector2(1f, 1f);
            content.pivot = new Vector2(0.5f, 1f);
            content.offsetMin = Vector2.zero;
            content.offsetMax = Vector2.zero;
            var layout = contentObject.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 10f;
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;
            contentObject.AddComponent<ContentSizeFitter>().verticalFit =
                ContentSizeFitter.FitMode.PreferredSize;
            scroll.viewport = viewport.rectTransform;
            scroll.content = content;
            return scroll;
        }

        public static RectTransform CreateCard(Transform parent)
        {
            Image image = CreateImage("Password", parent, Surface);
            var layout = image.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(18, 18, 14, 14);
            layout.spacing = 8f;
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;
            image.gameObject.AddComponent<ContentSizeFitter>().verticalFit =
                ContentSizeFitter.FitMode.PreferredSize;
            return image.rectTransform;
        }

        public static void Clear(Transform parent)
        {
            for (int index = parent.childCount - 1; index >= 0; index--)
                Object.Destroy(parent.GetChild(index).gameObject);
        }

        private static Font Font
        {
            get
            {
                if (_font == null)
                    _font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                return _font;
            }
        }

        private static Image CreateImage(string name, Transform parent, Color color)
        {
            GameObject imageObject = CreateObject(name, parent);
            var image = imageObject.AddComponent<Image>();
            image.color = color;
            return image;
        }

        private static GameObject CreateObject(string name, Transform parent)
        {
            var instance = new GameObject(name, typeof(RectTransform));
            instance.transform.SetParent(parent, false);
            return instance;
        }

        private static void AddLayout(GameObject target, float preferredHeight)
        {
            var layout = target.AddComponent<LayoutElement>();
            layout.preferredHeight = preferredHeight;
        }

        private static void Stretch(
            RectTransform rect,
            float left = 0f,
            float right = 0f,
            float bottom = 0f,
            float top = 0f)
        {
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = new Vector2(left, bottom);
            rect.offsetMax = new Vector2(-right, -top);
        }

        private static void EnsureEventSystem()
        {
            if (Object.FindObjectOfType<EventSystem>() != null)
                return;
            var eventSystem = new GameObject("EventSystem");
            eventSystem.AddComponent<EventSystem>();
            eventSystem.AddComponent<StandaloneInputModule>();
        }
    }
}
