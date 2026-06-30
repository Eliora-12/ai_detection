import { render, screen, fireEvent } from '@testing-library/react'
import ServerCard from '@/components/dashboard/ServerCard'
import '@testing-library/jest-dom'

const mockServer = {
  server_id: 'server1',
  status: 'ok' as const,
  cpu: 0.1,
  memory: 0.2,
  latency_ms: 50,
  error_rate: 0,
  request_count: 100,
  uptime_seconds: 3600,
  prediction: {
    server_id: 'server1',
    is_anomaly: false,
    fault_probability: 0.1,
    fault_type: 'healthy',
    recommended_action: 'none',
    confidence: 0.9,
    explanation: 'System is healthy',
    feature_importances: {}
  }
}

describe('ServerCard', () => {
  it('renders server info correctly', () => {
    render(<ServerCard serverId="server1" server={mockServer} onTrigger={() => {}} />)
    expect(screen.getByText('SERVER1')).toBeInTheDocument()
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('calls onTrigger when button clicked', () => {
    const onTrigger = jest.fn()
    const serverWithAction = {
      ...mockServer,
      prediction: { ...mockServer.prediction, recommended_action: 'restart' }
    }
    render(<ServerCard serverId="server1" server={serverWithAction} onTrigger={onTrigger} />)
    const button = screen.getByText('Trigger RESTART')
    fireEvent.click(button)
    expect(onTrigger).toHaveBeenCalledWith('server1', 'restart')
  })
})
