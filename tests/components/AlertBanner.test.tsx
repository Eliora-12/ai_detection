import { render, screen } from '@testing-library/react'
import AlertBanner from '@/components/dashboard/AlertBanner'

const mockPredictions = [
  {
    server_id: 'server2',
    is_anomaly: true,
    fault_probability: 0.85,
    fault_type: 'memory_leak',
    recommended_action: 'restart',
    confidence: 0.85,
    explanation: 'Memory usage rising rapidly',
    feature_importances: {}
  }
]

describe('AlertBanner', () => {
  it('does not render when no predictions cross threshold', () => {
    const { container } = render(<AlertBanner predictions={[]} threshold={0.6} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders correctly when threshold crossed', () => {
    render(<AlertBanner predictions={mockPredictions} threshold={0.6} />)
    expect(screen.getByText(/High Confidence Fault Predicted: SERVER2/i)).toBeInTheDocument()
    expect(screen.getByText(/Memory usage rising rapidly/i)).toBeInTheDocument()
  })
})
