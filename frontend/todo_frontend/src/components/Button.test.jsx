import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Button from './Button';

function CurrentPath() {
  const location = useLocation();
  return <output aria-label="current route">{location.pathname}</output>;
}

describe('Create button', () => {
  it('opens account creation', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Button />
        <CurrentPath />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Get started' }));

    expect(screen.getByLabelText('current route')).toHaveTextContent('/register');
  });
});
