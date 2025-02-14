// src/api/taskApi.js
import axios from 'axios';

const apiUrl = '/tasks/';

export const fetchTasks = (filters) => {
  return axios.get(apiUrl, { params: filters });
};

export const deleteTask = (taskId) => {
  return axios.delete(`${apiUrl}${taskId}/`);
};

export const completeTask = (taskId) => {
  return axios.patch(`${apiUrl}${taskId}/complete/`);
};

export const updateTask = (taskId, taskData) => {
  return axios.put(`${apiUrl}${taskId}/`, taskData);
};

export const createTask = (taskData) => {
  return axios.post(apiUrl, taskData);
};
