import React, { useState } from "react";
import axios from "axios";
import { ClipLoader } from "react-spinners";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const SettingsPage: React.FC = () => {
  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExport = async () => {
    if (!telegramUser?.id) return;

    setLoading(true);
    setError("");

    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/users/user-report`,
        {
          params: { telegram_id: telegramUser.id },
          responseType: "blob"
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `nutrition_report_${new Date().toISOString()}.txt`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();

    } catch (err) {
      setError("Ошибка при экспорте данных");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px 15px 80px" }}>
      <h2 style={{
        marginBottom: "24px",
        textAlign: "center",
        color: "var(--text-primary)",
        fontSize: "1.5rem"
      }}>
        Настройки
      </h2>

      {telegramUser ? (
        <div style={{
          marginBottom: "32px",
          textAlign: "center"
        }}>
          <h3 style={{
            color: "var(--text-primary)",
            fontSize: "1.2rem",
            marginBottom: "8px"
          }}>
            Привет, {telegramUser.first_name || telegramUser.username || "Пользователь"}!
          </h3>
          <p style={{
            color: "var(--text-secondary)",
            fontSize: "0.9rem"
          }}>
            ID: {telegramUser.id}
          </p>
        </div>
      ) : (
        <div style={{
          backgroundColor: "var(--surface-color)",
          padding: "16px",
          borderRadius: "var(--border-radius)",
          marginBottom: "20px",
          textAlign: "center"
        }}>
          <p>Нет данных о пользователе</p>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
            Откройте приложение через Telegram
          </p>
        </div>
      )}

      <div style={{
        maxWidth: "300px",
        margin: "0 auto"
      }}>
        <button
          onClick={handleExport}
          disabled={loading || !telegramUser}
          style={{
            width: "100%",
            padding: "14px 24px",
            backgroundColor: "var(--primary-color)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "8px",
            opacity: loading ? 0.7 : 1,
            fontSize: "1.1rem"
          }}
        >
          {loading ? (
            <ClipLoader color="#ffffff" size={20} />
          ) : (
            <>
              <span>📥</span>
              Экспорт данных
            </>
          )}
        </button>

        {error && (
          <div style={{
            marginTop: "16px",
            color: "#ff4444",
            textAlign: "center",
            fontSize: "0.9rem"
          }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;