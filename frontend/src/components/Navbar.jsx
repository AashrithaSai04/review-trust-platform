import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, UploadCloud, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

const Navbar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Analyze Review', path: '/prediction', icon: CheckSquare },
    { name: 'Batch Upload', path: '/upload', icon: UploadCloud },
    { name: 'Moderation', path: '/moderation', icon: ShieldAlert },
  ];

  return (
    <motion.nav 
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-68 backdrop-blur-xl bg-black/30 min-h-screen p-5 flex flex-col border-r border-white/5 relative z-20 shadow-[4px_0_24px_rgba(0,0,0,0.4)]"
    >
      <div className="flex items-center space-x-3 px-2 mb-12 mt-4 cursor-default">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-[0_0_15px_rgba(168,85,247,0.5)]">
          <ShieldAlert size={22} className="text-white relative z-10" />
        </div>
        <div>
          <h1 className="font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 text-xl tracking-tight">TrustScore<span className="text-purple-400">.ai</span></h1>
          <p className="text-[10px] text-purple-300/70 font-semibold tracking-widest uppercase">Admin Portal</p>
        </div>
      </div>

      <div className="flex-1 space-y-3">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `group relative flex items-center space-x-3 px-5 py-3.5 rounded-xl transition-all duration-300 overflow-hidden ${
                isActive 
                  ? 'text-white shadow-[0_0_20px_rgba(168,85,247,0.3)] bg-white/10 border border-white/10' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-md rounded-xl"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <div className="relative z-10 flex items-center space-x-3">
                  <item.icon size={20} className={`transition-transform duration-300 ${isActive ? 'text-purple-400 scale-110' : 'group-hover:scale-110'}`} />
                  <span className="font-semibold text-sm tracking-wide">{item.name}</span>
                </div>
              </>
            )}
          </NavLink>
        ))}
      </div>

      <div className="mt-auto px-1 py-6">
        <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 flex items-center space-x-4 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex-shrink-0 flex items-center justify-center text-white font-bold shadow-lg group-hover:shadow-purple-500/50 transition-all duration-300">
            AD
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-bold text-white truncate">Admin User</p>
            <p className="text-xs text-purple-300/70 truncate">admin@trustscore.ai</p>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
