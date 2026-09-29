import "./globals.css";

export const metadata = {
  title: "SupplyChain Sentinel",
  description: "Know which late delivery will stop your line, before it does."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
