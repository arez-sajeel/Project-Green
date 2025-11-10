import React from 'react';

const WelcomePage = () => {
  return (
    <div className="bg-green-50 flex items-center justify-center min-h-screen">
      <main className="bg-white rounded-xl shadow-lg p-8 text-center max-w-md w-full">
        <h1 className="text-4xl font-bold text-green-600 mb-2">Renewi</h1>
        <p className="text-pink-500 text-lg mb-6">
          An apple a day keeps the power bills away.
        </p>
        <img
          src= "renewi logo.png"
          alt="Renewi mascot waving"
          className="w-48 mx-auto mb-6"
        />
        <div className="flex justify-center gap-4">
          <button className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition">
            Login
          </button>
          <button className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition">
            Sign Up
          </button>
        </div>
      </main>
    </div>
  );
};

export default WelcomePage;