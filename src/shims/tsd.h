/*
 * Copyright (c) 2008-2013 Apple Inc. All rights reserved.
 *
 * @APPLE_APACHE_LICENSE_HEADER_START@
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @APPLE_APACHE_LICENSE_HEADER_END@
 */

/*
 * IMPORTANT: This header file describes INTERNAL interfaces to libdispatch
 * which are subject to change in future releases of Mac OS X. Any applications
 * relying on these interfaces WILL break.
 */

#ifndef __DISPATCH_SHIMS_TSD__
#define __DISPATCH_SHIMS_TSD__

#if HAVE_PTHREAD_MACHDEP_H
#include <pthread_machdep.h>
#endif

#if TARGET_OS_LINUX
#include <sched.h>
#endif

#define DISPATCH_TSD_INLINE DISPATCH_ALWAYS_INLINE_NDEBUG

#if USE_APPLE_TSD_OPTIMIZATIONS && HAVE_PTHREAD_KEY_INIT_NP && \
	!defined(DISPATCH_USE_DIRECT_TSD)
#define DISPATCH_USE_DIRECT_TSD 1
#if __has_include(<os/tsd.h>)
#include <os/tsd.h>
#endif
#endif

#if DISPATCH_USE_DIRECT_TSD
#define DISPATCH_TSD_DEFINE(...)
static const unsigned long dispatch_queue_key		= __PTK_LIBDISPATCH_KEY0;
#if DISPATCH_USE_OS_SEMAPHORE_CACHE
static const unsigned long dispatch_sema4_key		= __TSD_SEMAPHORE_CACHE;
#else
static const unsigned long dispatch_sema4_key		= __PTK_LIBDISPATCH_KEY1;
#endif
static const unsigned long dispatch_cache_key		= __PTK_LIBDISPATCH_KEY2;
static const unsigned long dispatch_io_key			= __PTK_LIBDISPATCH_KEY3;
static const unsigned long dispatch_apply_key		= __PTK_LIBDISPATCH_KEY4;
#if DISPATCH_INTROSPECTION
static const unsigned long dispatch_introspection_key = __PTK_LIBDISPATCH_KEY5;
#elif DISPATCH_PERF_MON
static const unsigned long dispatch_bcounter_key	= __PTK_LIBDISPATCH_KEY5;
#endif

#elif TARGET_OS_LINUX
#define DISPATCH_TSD_DECL(key_name)               \
	extern __thread uintptr_t key_name##_storage; \
	extern pthread_key_t key_name;                \
	extern void (*key_name##_finalizer)(void *);  \
	extern void key_name##_destructor(void *)

#define DISPATCH_TSD_DEFINE(key_name)                                 \
	void key_name##_destructor(void *p)                               \
	{                                                                 \
		(void) p;                                                     \
		void *_val = _dispatch_thread_getspecific(key_name);          \
		if (_val) key_name##_finalizer(_val);                         \
	}                                                                 \
	__thread __attribute__((                                          \
			tls_model("initial-exec"))) uintptr_t key_name##_storage; \
	pthread_key_t key_name = 0;                                       \
	void (*key_name##_finalizer)(void *) = NULL

#else
#define DISPATCH_TSD_DECL(key_name) extern pthread_key_t key_name
#define DISPATCH_TSD_DEFINE(key_name) pthread_key_t key_name
#endif

#if !DISPATCH_USE_DIRECT_TSD
DISPATCH_TSD_DECL(dispatch_queue_key);
#if DISPATCH_USE_OS_SEMAPHORE_CACHE
#error "Invalid DISPATCH_USE_OS_SEMAPHORE_CACHE configuration"
#else
DISPATCH_TSD_DECL(dispatch_sema4_key);
#endif
DISPATCH_TSD_DECL(dispatch_cache_key);
DISPATCH_TSD_DECL(dispatch_io_key);
DISPATCH_TSD_DECL(dispatch_apply_key);
#if DISPATCH_INTROSPECTION
DISPATCH_TSD_DECL(dispatch_introspection_key);
#elif DISPATCH_PERF_MON
DISPATCH_TSD_DECL(dispatch_bcounter_key);
#endif
#endif // !DISPATCH_USE_DIRECT_TSD

#if TARGET_OS_MAC
#if DISPATCH_USE_DIRECT_TSD
DISPATCH_TSD_INLINE
static inline void
_dispatch_thread_key_create(const unsigned long *k, void (*d)(void *))
{
	dispatch_assert_zero(pthread_key_init_np((int)*k, d));
}
#else
DISPATCH_TSD_INLINE
static inline void
_dispatch_thread_key_create(pthread_key_t k, void (*d)(void *))
{
	dispatch_assert_zero(pthread_key_create(k, d));
}
#endif // DISPATCH_USE_DIRECT_TSD

#if !DISPATCH_USE_TSD_BASE || DISPATCH_DEBUG
DISPATCH_TSD_INLINE
static inline void
_dispatch_thread_setspecific(pthread_key_t k, void *v)
{
#if DISPATCH_USE_DIRECT_TSD
	if (_pthread_has_direct_tsd()) {
		(void)_pthread_setspecific_direct(k, v);
		return;
	}
#endif
	dispatch_assert_zero(pthread_setspecific(k, v));
}

DISPATCH_TSD_INLINE
static inline void *
_dispatch_thread_getspecific(pthread_key_t k)
{
#if DISPATCH_USE_DIRECT_TSD
	if (_pthread_has_direct_tsd()) {
		return _pthread_getspecific_direct(k);
	}
#endif
	return pthread_getspecific(k);
}
#endif // !DISPATCH_USE_TSD_BASE || DISPATCH_DEBUG

#elif TARGET_OS_LINUX
#define _dispatch_thread_key_create(key_name, destructor)               \
	do {                                                                \
		*(key_name##_finalizer) = (destructor);                         \
		dispatch_assert_zero(                                           \
				pthread_key_create((key_name), key_name##_destructor)); \
	} while (0)

#define _dispatch_thread_getspecific(key_name) \
	(void *)(key_name##_storage & ~(uintptr_t)1)

#define _dispatch_thread_setspecific(key_name, v)                             \
	do {                                                                      \
		uintptr_t _old = key_name##_storage;                                  \
		key_name##_storage = (uintptr_t)(v) | 1u;                             \
		if (slowpath(_old == 0)) pthread_setspecific((key_name), (void *)1u); \
	} while (0)

#else
DISPATCH_TSD_INLINE
static inline void
_dispatch_thread_key_create(pthread_key_t *k, void (*d)(void *))
{
	dispatch_assert_zero(pthread_key_create(k, d));
}

DISPATCH_TSD_INLINE
static inline void
_dispatch_thread_setspecific(pthread_key_t k, void *v)
{
	dispatch_assert_zero(pthread_setspecific(k, v));
}

DISPATCH_TSD_INLINE
static inline void *
_dispatch_thread_getspecific(pthread_key_t k)
{
	return pthread_getspecific(k);
}
#endif // TARGET_OS_MAC

#if TARGET_OS_WIN32
#define _dispatch_thread_self() ((uintptr_t)GetCurrentThreadId())
#else
#if DISPATCH_USE_DIRECT_TSD
#define _dispatch_thread_self() ((uintptr_t)_dispatch_thread_getspecific( \
		_PTHREAD_TSD_SLOT_PTHREAD_SELF))
#else
#define _dispatch_thread_self() ((uintptr_t)pthread_self())
#endif
#endif

DISPATCH_TSD_INLINE DISPATCH_CONST
static inline unsigned int
_dispatch_cpu_number(void)
{
#if TARGET_IPHONE_SIMULATOR && IPHONE_SIMULATOR_HOST_MIN_VERSION_REQUIRED < 1090
	return 0;
#elif __has_include(<os/tsd.h>)
	return _os_cpu_number();
#elif TARGET_OS_LINUX
	int val = sched_getcpu();
	return val >= 0 ? (unsigned int)val : 0;
#elif defined(__x86_64__) || defined(__i386__)
	struct { uintptr_t p1, p2; } p;
	__asm__("sidt %[p]" : [p] "=&m" (p));
	return (unsigned int)(p.p1 & 0xfff);
#else
	// Not yet implemented.
	return 0;
#endif
}

#undef DISPATCH_TSD_INLINE

#endif
