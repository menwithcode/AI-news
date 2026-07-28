"use client";

import { useEffect, useState } from "react";

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

type Status = "unsupported" | "unsubscribed" | "subscribing" | "subscribed" | "denied";

export default function NotificationSubscribe() {
  const [status, setStatus] = useState<Status>("unsubscribed");

  useEffect(() => {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      setStatus("unsupported");
      return;
    }
    if (Notification.permission === "denied") {
      setStatus("denied");
      return;
    }
    navigator.serviceWorker.getRegistration("/sw.js").then(async (reg) => {
      const sub = await reg?.pushManager.getSubscription();
      if (sub) setStatus("subscribed");
    });
  }, []);

  async function handleSubscribe() {
    setStatus("subscribing");
    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setStatus("denied");
        return;
      }

      const registration = await navigator.serviceWorker.register("/sw.js");
      await navigator.serviceWorker.ready;

      const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
      if (!vapidPublicKey) {
        throw new Error("Missing NEXT_PUBLIC_VAPID_PUBLIC_KEY");
      }

      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      });

      await fetch("/api/push/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(subscription),
      });

      setStatus("subscribed");
    } catch (err) {
      console.error("Push subscribe failed:", err);
      setStatus("unsubscribed");
    }
  }

  if (status === "unsupported") return null;

  if (status === "subscribed") {
    return <span className="text-xs text-gray-400">Notifications on</span>;
  }

  if (status === "denied") {
    return (
      <span className="text-xs text-gray-400">Notifications blocked</span>
    );
  }

  return (
    <button
      onClick={handleSubscribe}
      disabled={status === "subscribing"}
      className="text-xs font-semibold text-blue-600 hover:text-blue-800 disabled:opacity-50"
    >
      {status === "subscribing" ? "Enabling..." : "Enable Notifications"}
    </button>
  );
}
