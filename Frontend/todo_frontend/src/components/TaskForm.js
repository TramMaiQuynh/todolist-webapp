import React, { useState, useEffect } from "react";
import axios from "axios";

const TaskForm = ({ taskId, onFormSubmit }) => {
  const [task, setTask] = useState({
    title: "",
    description: "",
    status: "Pending",
    priority: "Medium",
  });

  useEffect(() => {
    if (taskId) {
      const fetchTask = async () => {
        const response = await axios.get(`/tasks/${taskId}/`);
        setTask(response.data);
      };
      fetchTask();
    }
  }, [taskId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTask((prevTask) => ({
      ...prevTask,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (taskId) {
        await axios.put(`/tasks/${taskId}/`, task);
      } else {
        await axios.post("/tasks/", task);
      }
      onFormSubmit();
    } catch (error) {
      console.error("Error saving task", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="title"
        value={task.title}
        onChange={handleChange}
        placeholder="Task title"
      />
      <textarea
        name="description"
        value={task.description}
        onChange={handleChange}
        placeholder="Task description"
      />
      <select name="status" value={task.status} onChange={handleChange}>
        <option value="Pending">Pending</option>
        <option value="In_progress">In Progress</option>
      </select>
      <select name="priority" value={task.priority} onChange={handleChange}>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
      </select>
      <button type="submit">{taskId ? "Update Task" : "Create Task"}</button>
    </form>
  );
};

export default TaskForm;
