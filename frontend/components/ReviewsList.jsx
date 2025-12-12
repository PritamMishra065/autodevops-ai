import React, { useState, useEffect } from 'react'
import { RefreshCw, Star, MessageSquare, CheckCircle2, XCircle } from 'lucide-react'
import { apiService } from '../services/api'

const ReviewsList = () => {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchReviews = async () => {
    setLoading(true)
    try {
      const response = await apiService.getReviews()
      const reviewData = response.data || []
      setReviews(reviewData)
    } catch (error) {
      console.error('Error fetching reviews:', error)
      setReviews([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReviews()
    const interval = setInterval(fetchReviews, 10000)
    return () => clearInterval(interval)
  }, [])

  const getReviewStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
      case 'accepted':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'rejected':
      case 'declined':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <MessageSquare className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Star className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-gray-800">Code Reviews</h2>
        </div>
        <button
          onClick={fetchReviews}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="space-y-4">
        {reviews.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {loading ? 'Loading reviews...' : 'No reviews available'}
          </div>
        ) : (
          reviews.map((review, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  {getReviewStatusIcon(review.status)}
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      {review.title || review.pull_request || 'Code Review'}
                    </h3>
                    {review.reviewer && (
                      <p className="text-sm text-gray-600">
                        Reviewed by: {review.reviewer}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">
                    {review.timestamp || review.created_at || 'Unknown time'}
                  </div>
                  {review.rating && (
                    <div className="flex items-center gap-1 mt-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < review.rating
                              ? 'text-yellow-400 fill-current'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
              {review.comments && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">{review.comments}</p>
                </div>
              )}
              {review.suggestions && review.suggestions.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-semibold text-gray-600 mb-1">
                    Suggestions:
                  </p>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {review.suggestions.map((suggestion, idx) => (
                      <li key={idx}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ReviewsList

