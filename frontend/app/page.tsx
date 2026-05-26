"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
export default function Home() {
  const router = useRouter()
  useEffect(() => { router.push(localStorage.getItem('token') ? '/dashboard/chat' : '/login') }, [])
  return null
}
