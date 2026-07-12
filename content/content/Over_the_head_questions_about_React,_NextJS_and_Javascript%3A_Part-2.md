---
date: '2026-05-22'
tags:
- web-dev
description: Part two of covering questions as newcomer to react and Nextjs.
lang:
- js
- html
---

#[[Blog Posts]]  
  
Why are images and fonts served as static assets, and how does this improve loading performance?
logseq.order-list-type:: number
How does Next.js `<Link>` enable navigation without a full page reload? What is client-side routing?
logseq.order-list-type:: number
How do React hooks like `useState` and `useEffect` work conceptually under the hood?
logseq.order-list-type:: number
Why does running logic on the server in Next.js reduce the surface area for security vulnerabilities?
logseq.order-list-type:: number
What are Server Actions in Next.js, and how do they simplify server-side mutations?
logseq.order-list-type:: number
How do I understand this Next.js Page function signature and inline TypeScript type?
logseq.order-list-type:: number
	-
	  ```js
	  export default async function Page(props: {
	    searchParams?: Promise<{
	      query?: string;
	      page?: string;
	    }>;
	  }) {
	    const searchParams = await props.searchParams;
	    const query = searchParams?.query || "";
	    const currentPage = Number(searchParams?.page) || 1;
	  	// Reamining code
	  }
	  ```
