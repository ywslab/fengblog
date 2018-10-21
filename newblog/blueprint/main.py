from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, send_from_directory
from flask_login import current_user
from newblog.models import Post, Category, User, Comment, db
from newblog.forms import CommentForm


main = Blueprint('main', __name__)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NEWBLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('main/index.html', pagination=pagination, posts=posts)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NEWBLOG_COMMENT_PER_PAGE']
    if current_user == post.author:
        pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.asc()).paginate(page, per_page)
    else:
        pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(
            Comment.timestamp.asc()).paginate(
            page, per_page)
    comments = pagination.items
    form = CommentForm()
    from_author = False
    reviewed = False
    from_admin = False
    if form.validate_on_submit():
        author = current_user.username
        body = form.body.data
        if post.author.username == author:  # rename problem
            from_author = True
            reviewed = True

        if current_user.is_administrator():
            reviewed = True
            from_admin = True
        comment = Comment(author=author, body=body, from_author=from_author, post=post, reviewed=reviewed,
                          from_admin=from_admin)
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()
        if post.author.username == author:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            # send_new_comment_email(post)  # send notification email to editor
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('main/post.html', post=post, pagination=pagination, form=form, comments=comments)


@main.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NEWBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/category.html', category=category, pagination=pagination, posts=posts)


@main.route('/about')
def about():
    return render_template('main/about.html')


@main.route('/<int:userid>')
def editor(userid):
    editor = User.query.filter_by(id = userid).first()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['NEWBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(editor).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/author.html', editor=editor, pagination=pagination, posts=posts)
