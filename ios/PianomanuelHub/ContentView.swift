import SwiftUI
import WebKit

/// Loads the compiled site from the app bundle. No remote hub. No secrets.
struct ContentView: View {
    var body: some View {
        HubWebView()
            .ignoresSafeArea()
    }
}

struct HubWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        let view = WKWebView(frame: .zero, configuration: config)
        view.scrollView.bounces = false
        if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "site") {
            view.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        } else if let url = Bundle.main.url(forResource: "index", withExtension: "html") {
            view.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return view
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
