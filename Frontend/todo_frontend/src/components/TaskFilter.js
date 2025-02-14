import React from "react";

const TaskFilter = ({ setFilters }) => {
  const handleStatusChange = (e) => {
    setFilters((prev) => ({
      ...prev,
      status: e.target.value,
    }));
  };

  const handlePriorityChange = (e) => {
    setFilters((prev) => ({
      ...prev,
      priority: e.target.value,
    }));
  };

  return (
    <div>
      <label>Status: </label>
      <select onChange={handleStatusChange}>
        <option value="All">All</option>
        <option value="Pending">Pending</option>
        <option value="In_progress">In Progress</option>
        <option value="Completed">Completed</option>
      </select>

      <label>Priority: </label>
      <select onChange={handlePriorityChange}>
        <option value="All">All</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
      </select>
    </div>
  );
};

export default TaskFilter;
