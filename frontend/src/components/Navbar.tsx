import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar({ onOpenMenu, onOpenSignIn }: { onOpenMenu: () => void, onOpenSignIn: () => void }) {
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('home');

  useEffect(() => {
    const scrollContainer = document.getElementById('main-scroll');
    if (!scrollContainer) return;
    
    const handleScroll = () => {
      setIsScrolled(scrollContainer.scrollTop > 50);
    };
    
    scrollContainer.addEventListener('scroll', handleScroll);

    // Setup Intersection Observer for active section highlighting
    const sections = ['home', 'route', 'warehouses', 'weather', 'analytics', 'dashboard', 'about'];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
            // Optionally update the URL silently so refreshes keep position
            window.history.replaceState(null, '', `#${entry.target.id}`);
          }
        });
      },
      // rootMargin "-40% 0px -60% 0px" means the section only needs to cross the horizontal line slightly above the center of the screen to become active.
      // This prevents tall sections (like Warehouses) from being skipped when they are larger than 100vh.
      { root: scrollContainer, rootMargin: "-40% 0px -50% 0px", threshold: 0 } 
    );

    sections.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => {
      scrollContainer.removeEventListener('scroll', handleScroll);
      observer.disconnect();
    };
  }, []);

  const navLinks = [
    { name: 'HOME', path: '#home' },
    { name: 'SMART ROUTE', path: '#route' },
    { name: 'WAREHOUSE', path: '#warehouses' },
    { name: 'WEATHER', path: '#weather' },
    { name: 'ML ANALYTICS', path: '#analytics' },
    { name: 'DASHBOARD', path: '#dashboard' },
    { name: 'ABOUT US', path: '#about' },
  ];

  return (
    <motion.nav 
      initial={false}
      animate={{
        paddingTop: isScrolled ? '0.75rem' : '1.5rem',
        paddingBottom: isScrolled ? '0.75rem' : '1.5rem',
        backgroundColor: isScrolled ? 'rgba(0, 0, 0, 0.85)' : 'rgba(0, 0, 0, 0)',
        backdropFilter: isScrolled ? 'blur(16px)' : 'blur(0px)'
      }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className={clsx(
        "fixed top-0 w-full z-50 px-8 md:px-12 flex items-center justify-between text-white transition-all duration-500",
        isScrolled && "border-b border-white/10 shadow-2xl"
      )}
    >
      {/* Left: Logo (takes equal space to keep center balanced) */}
      <div className="flex flex-1 justify-start">
        <AnimatePresence>
          {!isScrolled && (
            <motion.a 
              href="#home" 
              className="flex flex-col tracking-tight overflow-hidden"
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.3 }}
            >
              <span className="font-bold text-2xl lg:text-3xl tracking-widest italic whitespace-nowrap">ROUTESHIELD</span>
              <span className="text-[9px] lg:text-[10px] tracking-[0.2em] font-bold italic mt-0.5 whitespace-nowrap text-blue-400">AI ROAD INTELLIGENCE</span>
            </motion.a>
          )}
        </AnimatePresence>
      </div>
      
      {/* Middle: Links */}
      <motion.div 
        animate={{
          gap: isScrolled ? '1rem' : '1.5rem',
          fontSize: isScrolled ? '0.7rem' : '0.75rem'
        }}
        transition={{ duration: 0.4, ease: "easeInOut" }}
        className="hidden lg:flex flex-auto justify-center items-center font-bold tracking-widest uppercase"
      >
        {navLinks.map((link) => {
          const isActive = activeSection === link.path.substring(1);
          return (
            <a 
              key={link.name} 
              href={link.path}
              className={clsx(
                "relative pb-2 hover:opacity-80 transition-opacity text-white whitespace-nowrap"
              )}
            >
              {link.name}
              {isActive && (
                <motion.span 
                  layoutId="activeNavLine"
                  className="absolute left-0 bottom-0 w-full h-[3px] bg-blue-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.9)]" 
                  transition={{ type: "spring", stiffness: 400, damping: 35 }}
                />
              )}
            </a>
          );
        })}
      </motion.div>

      {/* Right: Actions */}
      <div className="flex flex-1 justify-end items-center gap-4">
        <button 
          onClick={onOpenMenu} 
          className="text-white hover:opacity-80 transition-opacity font-bold tracking-widest text-xs lg:hidden"
        >
          MENU
        </button>
        <motion.button 
          animate={{
            padding: isScrolled ? '0.35rem 1rem' : '0.5rem 1.25rem',
            fontSize: isScrolled ? '0.75rem' : '0.8rem'
          }}
          transition={{ duration: 0.3 }}
          onClick={onOpenSignIn}
          className="bg-white text-black rounded-full font-bold tracking-widest hover:bg-gray-200 transition-colors whitespace-nowrap"
        >
          LOGIN
        </motion.button>
      </div>
    </motion.nav>
  );
}
