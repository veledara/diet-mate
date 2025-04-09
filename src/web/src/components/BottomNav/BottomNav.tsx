import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiHome,
  FiBarChart2,
  FiThumbsUp,
  FiAward,
  FiSettings
} from 'react-icons/fi';
import styles from './BottomNav.module.css';

export const BottomNav: React.FC = () => {
  return (
    <nav className={styles.nav}>
      <NavLink
        to="/"
        end
        className={({ isActive }) =>
          `${styles.item} ${isActive ? styles.active : ''}`
        }
      >
        <FiHome className={styles.icon} size={30} />
        <span>Сегодня</span>
      </NavLink>

      <NavLink
        to="/analytics"
        className={({ isActive }) =>
          `${styles.item} ${isActive ? styles.active : ''}`
        }
      >
        <FiBarChart2 className={styles.icon} size={30} />
        <span>Аналитика</span>
      </NavLink>

      <NavLink
        to="/recommendations"
        className={({ isActive }) =>
          `${styles.item} ${isActive ? styles.active : ''}`
        }
      >
        <FiThumbsUp className={styles.icon} size={30} />
        <span>Рекомендации</span>
      </NavLink>

      <NavLink
        to="/achievements"
        className={({ isActive }) =>
          `${styles.item} ${isActive ? styles.active : ''}`
        }
      >
        <FiAward className={styles.icon} size={30} />
        <span>Достижения</span>
      </NavLink>

      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `${styles.item} ${isActive ? styles.active : ''}`
        }
      >
        <FiSettings className={styles.icon} size={30} />
        <span>Настройки</span>
      </NavLink>
    </nav>
  );
};