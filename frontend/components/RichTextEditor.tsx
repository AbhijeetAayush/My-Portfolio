'use client'

import { useMemo } from 'react'
import dynamic from 'next/dynamic'
import 'react-quill/dist/quill.snow.css'

// Dynamically import ReactQuill to avoid SSR issues
const ReactQuill = dynamic(() => import('react-quill'), { ssr: false })

interface RichTextEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export default function RichTextEditor({
  value,
  onChange,
  placeholder = 'Write your blog post...',
}: RichTextEditorProps) {
  const modules = useMemo(
    () => ({
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],
        ['link', 'image'],
        [{ color: [] }, { background: [] }],
        ['clean'],
      ],
    }),
    []
  )

  return (
    <div className="bg-white">
      <ReactQuill
        theme="snow"
        value={value}
        onChange={onChange}
        modules={modules}
        placeholder={placeholder}
        className="min-h-[400px]"
      />
    </div>
  )
}
