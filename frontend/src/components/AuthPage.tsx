import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-page">
      <div className="auth-content">
        <div className="auth-header">
          <h1>AI Agent Platform</h1>
          <p>Welcome to your AI assistant platform</p>
        </div>
        {isLogin ? (
          <LoginForm
            onSwitchToRegister={() => setIsLogin(false)}
          />
        ) : (
          <RegisterForm
            onSwitchToLogin={() => setIsLogin(true)}
          />
        )}
      </div>
    </div>
  );
};

export default AuthPage; 