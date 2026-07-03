  id:: 6931ab34-aad0-4894-8d44-3c07d3da0924
  public:: true
  date:: 2026-04-19
  tags:: web-dev
  description:: In this blog post I go along misconceptions and confusions I had when learning react, Nextjs and Javascript.
  lang:: js, html
#[[Blog Posts]]  
  
- Recently, I went through the labyrinth of web technologies. As someone who hasn't made any webapp before with JavaScript, it was indeed a roller coaster ride. I first made a web application in HTML, CSS and Flask. It was easy. Then came the need for dynamic nature in clients, attached with this fact came JavaScript and its numerous frameworks. Though, I studied the 2 most common technologies in web-dev world, namely React and Nextjs. As a new comer to the language, as well as to these frameworks, I had a lot of beginner questions regarding their architecture, file handling, routers etc. Some of these questions I am going to answer here. So, hang tight and read through this blog to see if there are some nuances you might have missed.
- # How is React different from Next.js? What problems do they solve separately?
- Actually they are not different. Rather one can be though of as a subset of other. So, React is a library of javascript that is used for creating interactive user interfaces(UIs). So, the contents that are to be rendered are broken down as something called react components which is then rendered accordingly.
-
- Traditionally, the library was built for SPAs, i.e. Single Page Applications. Nextjs is a framework of react that extends its capabilities to Multi-page interfraces. Not only this, Nextjs also extends into all the side jobs like image rendering optimisation, font caching, page routing, data fetching and even to server side components. So, Nextjs, builds upon react for providing a person with the means to create a full blown web application.
-
- Even though, the above image gives you a somewhat correct notion about the relation of these terms with each other, I wouldn't go about thinking them as it is. Because even though react is a js  library, it uses JSX(more on that later), even though Nextjs is a framework of react, it extends itself into a lot of other spaces (which can make it difficult to understand if you see Nextjs just as a UI framework). So, it is important to keep in mind that these things are more than just being a subset of one another.
- # Why do React developers use JSX? How is it better than writing separate HTML and JavaScript files?
- This question is more about the working and history of react than its technical details, yet I find it necessary to answer so that the fundamentals of how react works remain clear. JSX was made to be used in react. The question is why invent a new syntax extension of javascript just to be used by a  library.
- The answer lies in fact of how react differs from previous styles of writing web application. Traditionally, apps were created with a linear flow of logic, so you defined what changes how. But with complex UI behaviours (like infinite scroll, likes, searches, dynamic rendering on data fetching, video streaming) came into being, it became difficult to maintain the old style of writing code. React levelled this gap by breaking UI into components. Where each JSX function/react component follows three simple rules.
	- Any JSX  function should ultimately return a **single** tag, which you can wrap around `<div>` in most cases but can also use an empty tag, called fragment tag `<>` used for grouping tags.
	  logseq.order-list-type:: number
	- Close all tags explicitly, even tags like`<img>` and `<li>` also needs to be closed.
	  logseq.order-list-type:: number
	- Use camel case for all the variables and components as code ultimately converts to javascript which have restrictions on identifier(this rule is discussed after the note on DOM).
	  logseq.order-list-type:: number
- So, you could use these components repetitively if needed and a single piece of UI have all its working contained into a single component. It is different from how previously styling used to be stored in CSS files, UI structure in HTML and business logic in javascript files.
-
- Now, most important benefit of JSX hides in its third rule. It gets into how JSX is parsed/transformed internally by react. There was a common misconception I had about how JSX is processed internally. I thought that JSX might be converted into separate files where the return value went into html and the code logic into separate js files. But actually, the JSX syntax converts the return types into  JS function calls. So something like following:
	-
	  ```html
	  //jsx
	  <div className="greeting">
	    <h1>Hello, {name}!</h1>
	  </div>
	  ```
	- Changes into:
	  ```js
	  React.createElement('div', {className: 'greeting'},
	    React.createElement('h1', null, 'Hello, ', name, '!')
	  )
	  ```
	- At runtime, these function calls create plain JS objects that describe how the UI looks like.
	  Ex:  
	  ```json
	  {
	    type: 'div',
	    props: {
	      className: 'greeting',
	      children: {
	        type: 'h1',
	        props: {
	          children: ['Hello, ', name, '!']
	        }
	      }
	    }
	  }
	  ```
	- And hence the 3rd rule to name variables in camel case as they are ultimately converted to js objects. There are minor details about virtual DOM in play but that resides in deeper details of how react render its components (more on that in the last question).
- I always thought JSX combined js and html but normally the content returned by a component never gets converted to html directly. The syntax was chosen similar to HTML merely to maintain familiarity about how the UI structure syntax was defined in react.
- # What is the difference between state and props in React?
- This is a very common pitfall when understanding react (more so if you are new to javascript). So, what are states and props in react. Let's talk about each, one by one.
- Props or properties in React are simple. I like to think of them as pipelines. Something which brings in information, unchanged. There are a few nuances to keep in mind regarding `props`.
	- `props` is an argument for a component.
	  logseq.order-list-type:: number
	- `props` are ready-only in nature. Hence, a component can't change its own props.
	  logseq.order-list-type:: number
	- Each component receives a single `props` argument where the object itself can contain multiple properties, often accessed through object destructuring.
	  logseq.order-list-type:: number
	- They are passed on from parent component and generally used to customise/configure a component.
	  logseq.order-list-type:: number
- To give an example, look at the following code.
  ```jsx
  function Parent() {
    return <Greeting name="John Doe" />;
  }
  
  function Greeting({ name }) {
    return <h1>Hello, {name}</h1>;
  }
  ```
- Here `Parent` calls `Greeting` with property called `name` with value `John Doe`. The component `Greeting` excepts the prop and passes it onto its own `<h1>` tag. Hence, something defined above in `Parent` percolates down to child components using react properties.
- It is important to note that `name` here is enclosed in curly parenthesis, which is nothing but object destructuring. The above code is same as following.
  ```jsx
  function Greeting(props) {
    const name = props.name;
    return <h1>Hello, {name}</h1>;
  }
  ```
- Inheriting its behaviour from JS, if you pass props that are not used/defined, they are simply ignored. If you don't pass something that is needed. It leads to undefined behaviour.
-
- Now, coming to state. "State" is simply some memory space which stores some configurations of your application. Like:
	* Has a user logged in as student, teacher or admin?
	* Is the person viewing the application in dark or light mode?
	* Is a form filled or not?  
This data is stored and should be changeable by UI. Also, the UI must change according to changes in state. For smoothing the process of integrating UI and business logic with state variables, react provides a `useState` function. It takes a default value and returns a value representing the state and a setter function of the state.
	  ```js
// Example
const [theme, setTheme] = React.useState("dark");
	  ```

- But why not simply store the value in variables? One can do so but then there remains no way to notify a change in the value of the variable to react. Hence, no way to update UI. So, in a general application flow, parent components create and store states and pass them to child components as properties.
-
    Parent Component -> State -> Pass as props -> Child Component
    
- A typical example looks like following:
  ```jsx
  function Parent() {
    // Creating a state Variable with `useState`
    const [theme, setTheme] = React.useState("dark");
  
    // Passing the state as property of Child
    return <Child theme={theme} />;
  }
  
  // taking in theme property and using it for internal logic.
  function Child({ theme }) {
    return <div className={theme}>Hello</div>;
  }
  ```
- # Why do we need dynamic class names in React, and how does `clsx` library help manage them?
- This was a very common  doubt I had when dealing with react. I never initially understood the need of adding a whole new library just so that I can manage classes of a UI component. Moreover, most of the dynamicity is provided by tailwind so I wouldn't need to worry about the website being rendered properly on different devices.
- The issue arrives with the fact that tailwind has no way to see through the state (variables) of your application. For, example maybe there is a button that needs to have 3 different colours based on if the user is authenticated, if the feature is enabled and if a previous text-field is filled or not. Scenarios like these create the need for inclusion of `clsx`.
- So, it can do something like following.
  ```jsx
  <button
    className={clsx(
      "px-4 py-2 rounded",
      isActive ? "bg-blue-500 text-white" : "bg-gray-200 text-black",
      isDisabled && "opacity-50 cursor-not-allowed"
    )}
  >
    Click
   </button>
  ```
- One can quickly argue that something similar can be achieved without clsx, just by using ternary operators, so the above code looks like following without `clsx`.
  ```jsx
  <button
    className={`px-4 py-2 rounded
      ${isActive ? "bg-blue-500 text-white" : "bg-gray-200 text-black"}
      ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}
    `}
  >
    Click
  </button>
  ```
- It doesn't look any different, rather it is easier to make sense of. but as web applications grow in their size, conditional class names become inevitable, in such cases the ternary nesting becomes difficult to understand. Also, clsx ensures explicit mutual exclusivity between classes, so you don't mix-up classes by their order or get undefined behaviour when classes for different states are slightly over-lapping.
- For an example, let's take the following class for the example mentioned above.
  ```jsx
  className={`px-4 py-2 rounded
    ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}
    ${isActive ? "bg-blue-500 text-white" : "bg-gray-200 text-black"}
  `}
  ```
- Now, a small change is proposed.
  > Disabled buttons should **always** look gray, even if active.  
- To achieve this you make the following change.
  ```jsx
  ${isDisabled && "bg-gray-200 text-black opacity-50"}
  ${isActive && "bg-blue-500 text-white"}
  ```
- Notice the resultant class when both are true, this is how the `className` gets resolved.
  ```jsx
  bg-gray-200 text-black opacity-50 bg-blue-500 text-white
  ```
- Notice, this is not ergonomic in itself as we are unknowingly setting background(`bg`) colour twice. Also this code won't result in right output because when a property is set more than once, tailwind resolves it by considering the last setting. So, the order in which the conditions are defined is having effect on output class. Here, we can make the conditionals mutually exclusive with following code.
  ```jsx
  className={clsx(
    "px-4 py-2 rounded",
    {
      "bg-blue-500 text-white": isActive && !isDisabled,
      "bg-gray-200 text-black opacity-50": isDisabled,
    }
  )}
  ```
- Now, the rule is encoded and not implied by string order. This example proves the usefulness of clsx in situations where mutual exclusivity between conditions need to be ensured.
- # What is hydration, and why does Next.js need it for client components?
- Understanding hydration clears the path for understanding how react manipulates the UI. The need to understand hydration came when dealing with `Hydration error`. So, we have made the ground that JSX converts to plain js objects (which describe the UI in a loose sense). From here, the cross-platform nature of comes into play. How react is actually transformed depends on which platform it is running, and hence the kind of renderer that is used. Different places require different renderers, here are a few common examples.
  | Platform | Renderer |
  | Server Side Rendering | react-dom/server |
  | Client-Side Rendering | react-dom/client |
  | Native-Rendering(iOS, Android, Windows) | react-native |
  | Terminal-Rendering | Ink |
- Now, when the content is renderer in Server, it uses `react-dom/server`, this server converts js objects of react into html before transferring it to client. On the client, React recreates the virtual component tree and attempts to match it against the existing DOM produced by the server. During hydration, React expects the structure and content to match exactly and attaches event listeners and state without mutating the DOM.
- This initial matching of the React virtual tree with the existing DOM, along with attaching event listeners and initializing state, is called hydration. Hydration error occurs in scenarios when react expects no change between them but there are changes. For example, check the following code:
  ```jsx
  "use client";
  
  export function Time() {
    return <p>{Date.now()}</p>;
  }
  ```
- When server passes this to client, it renders `<p>1707460000000</p>`, but the client expects `<p>1707460000123</p>`. Here, the time lag creates a Hydration error.
- # Conclusion
- In this blog, we talked about react and Nextjs, how it works, some common issue which new comers face and their solutions. I would love to hear your input on the post. There will also be a part 2 of this blog releasing  soon. Till then, happy coding!!
