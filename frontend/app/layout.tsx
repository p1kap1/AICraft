import "./globals.css";
import { ThemeProvider } from "./providers";
export const metadata = { title: "AICraft" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="bg-white dark:bg-slate-900 text-slate-900 dark:text-white antialiased">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
