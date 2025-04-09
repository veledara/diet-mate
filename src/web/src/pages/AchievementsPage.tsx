import React, { useEffect, useState } from "react";
import axios from "axios";
import { ClipLoader } from "react-spinners";

interface Achievement {
  code: string;
  name: string;
  description: string;
  icon_url: string;
  unlocked_at: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const AchievementsPage: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const telegramId = telegramUser?.id;

  useEffect(() => {
    const fetchAchievements = async () => {
      if (!telegramId) {
        setError("Пользователь не найден.");
        return;
      }

      try {
        const response = await axios.get(
          `${API_BASE_URL}/api/v1/achievements/`,
          { params: { telegram_id: telegramId } }
        );

        setAchievements(response.data.achievements);
      } catch (err) {
        setError("Не получилось загрузить данные о достижениях:(");
      } finally {
        setLoading(false);
      }
    };

    fetchAchievements();
  }, [telegramId]);

  const unlockedCount = achievements.filter(a => a.unlocked_at !== null).length;
  const totalCount = achievements.length;

  if (loading) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh"
      }}>
        <ClipLoader color="#7c3aed" size={35} />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: "20px",
        textAlign: "center",
        color: "#ff4444"
      }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "20px 15px 80px" }}>
      <h2 style={{
        marginBottom: "24px",
        textAlign: "center",
        color: "var(--text-primary)",
        fontSize: "1.5rem"
      }}>
        Достижения
      </h2>

      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px",
        marginBottom: "20px"
      }}>
        <h3 style={{
          marginBottom: "16px",
          color: "var(--text-primary)"
        }}>
          Прогресс ({unlockedCount}/{totalCount})
        </h3>

        <div style={{
          width: "100%",
          height: "10px",
          backgroundColor: "var(--divider-color)",
          borderRadius: "5px"
        }}>
          <div
            style={{
              width: `${(unlockedCount / totalCount) * 100}%`,
              height: "100%",
              backgroundColor: "var(--primary-color)",
              borderRadius: "5px",
              transition: "width 0.3s ease"
            }}
          />
        </div>
      </div>

      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px",
        marginBottom: "20px"
      }}>
        <h3 style={{
          marginBottom: "16px",
          color: "var(--text-primary)"
        }}>
          Полученные достижения
        </h3>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
          gap: "16px"
        }}>
          {achievements
            .filter(a => a.unlocked_at)
            .map(achievement => (
              <div
                key={achievement.code}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "8px"
                }}
              >
                <img
                  src={`http://localhost:8000${achievement.icon_url}`}
                  alt={achievement.name}
                  style={{
                    width: "64px",
                    height: "64px",
                    objectFit: "contain"
                  }}
                />
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontWeight: 500 }}>{achievement.name}</div>
                  <div style={{
                    fontSize: "0.8em",
                    color: "var(--text-secondary)"
                  }}>
                    {achievement.description}
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px"
      }}>
        <h3 style={{
          marginBottom: "16px",
          color: "var(--text-primary)"
        }}>
          Предстоящие достижения
        </h3>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
          gap: "16px"
        }}>
          {achievements
            .filter(a => !a.unlocked_at)
            .map(achievement => (
              <div
                key={achievement.code}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "8px",
                  opacity: 0.6
                }}
              >
                <img
                  src={`http://localhost:8000${achievement.icon_url}`}
                  alt={achievement.name}
                  style={{
                    width: "64px",
                    height: "64px",
                    objectFit: "contain",
                    filter: "grayscale(100%)"
                  }}
                />
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontWeight: 500 }}>{achievement.name}</div>
                  <div style={{
                    fontSize: "0.8em",
                    color: "var(--text-secondary)"
                  }}>
                    {achievement.description}
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default AchievementsPage;