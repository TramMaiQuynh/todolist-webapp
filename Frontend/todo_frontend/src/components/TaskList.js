import React, { useState, useEffect } from "react";
import axios from "axios";
import TaskItem from "./TaskItem";
import TaskFilter from "./TaskFilter";

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [filters, setFilters] = useState({
    status: "All",
    priority: "All",
  });

  // Fetch tasks từ API
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/v1/tasks/", {
          params: filters,
        });
        setTasks(response.data);
      } catch (error) {
        console.error("There was an error fetching tasks!", error);
      }
    };

    fetchTasks();
  }, [filters]);

  // Hàm xử lý xóa task trong danh sách
  const handleDeleteTask = (deletedTaskId) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== deletedTaskId));
  };

  return (
    <div>
      <h1>Task List</h1>
      <TaskFilter setFilters={setFilters} />
      <ul>
        {tasks.map((task) => (
          <TaskItem key={task.id} task={task} onDelete={handleDeleteTask} />
        ))}
      </ul>
    </div>
  );
};

export default TaskList;
