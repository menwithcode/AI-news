import "./globals.css";

export const metadata = {
  title: "AI Update Hub",
  description: "Personal AI news, research, and GitHub repo aggregator",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 antialiased">{children}</body>
    </html>
  );
}
