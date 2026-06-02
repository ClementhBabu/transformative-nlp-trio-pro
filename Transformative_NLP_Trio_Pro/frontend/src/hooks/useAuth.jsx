import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUser = async () => {
      const savedToken = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      if (savedToken && savedUser) {
        try {
          const response = await authAPI.getProfile();
          setUser(response.data);
          localStorage.setItem('user', JSON.stringify(response.data));
        } catch {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    loadUser();
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user: userData } = response.data;
      const tokenValue = access_token || response.data.token;
      setToken(tokenValue);
      setUser(userData);
      localStorage.setItem('token', tokenValue);
      localStorage.setItem('user', JSON.stringify(userData));
      toast.success('Logged in successfully!');
      navigate('/dashboard');
    } catch (error) {
      const msg = error.response?.data?.detail || error.response?.data?.message || 'Login failed';
      toast.error(msg);
      throw error;
    }
  }, [navigate]);

  const register = useCallback(async (data) => {
    try {
      const response = await authAPI.register(data);
      const { access_token, user: userData } = response.data;
      const tokenValue = access_token || response.data.token;
      setToken(tokenValue);
      setUser(userData);
      localStorage.setItem('token', tokenValue);
      localStorage.setItem('user', JSON.stringify(userData));
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      const msg = error.response?.data?.detail || error.response?.data?.message || 'Registration failed';
      toast.error(msg);
      throw error;
    }
  }, [navigate]);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
    toast.success('Logged out');
  }, [navigate]);

  const updateProfile = useCallback(async (data) => {
    try {
      const response = await authAPI.updateProfile(data);
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      toast.success('Profile updated!');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Update failed';
      toast.error(msg);
      throw error;
    }
  }, []);

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
